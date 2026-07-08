import pytest
import typer

from fivemanager import cli
from fivemanager.cli import _alias_notice, console_command


def test_alias_notice_exists():
    assert callable(_alias_notice)


def test_console_command_for_stopped_server_exits_cleanly(monkeypatch):
    server = {"id": 1, "name": "Dev Survival", "key": "devsurvival"}
    messages = []

    monkeypatch.setattr(cli, "require_config", lambda: {"servers": [server]})
    monkeypatch.setattr(cli, "get_server", lambda config, server_id: server)
    monkeypatch.setattr(cli, "session_exists", lambda name: False)
    monkeypatch.setattr(cli, "warn", messages.append)
    monkeypatch.setattr(cli, "info", messages.append)
    monkeypatch.setattr(cli, "attach_console", lambda server: (_ for _ in ()).throw(AssertionError("attach_console should not be called")))

    with pytest.raises(typer.Exit) as exc:
        console_command(1)

    assert exc.value.exit_code == 0
    assert any("not running" in msg for msg in messages)
    assert any("fivemanager start 1" in msg for msg in messages)


def test_console_command_does_not_rich_print_before_tmux_attach(monkeypatch):
    server = {"id": 1, "name": "Dev Survival", "key": "devsurvival"}
    attached = []

    monkeypatch.setattr(cli, "require_config", lambda: {"servers": [server]})
    monkeypatch.setattr(cli, "get_server", lambda config, server_id: server)
    monkeypatch.setattr(cli, "session_exists", lambda name: True)
    monkeypatch.setattr(cli.console, "print", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("console attach path must not use Rich output before exec")))
    monkeypatch.setattr(cli, "attach_console", lambda attached_server: attached.append(attached_server))

    console_command(1)

    assert attached == [server]
