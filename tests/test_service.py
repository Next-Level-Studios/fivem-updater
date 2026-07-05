import pytest

from updatefivem.service import render_systemd_unit, validate_service_name


def test_render_systemd_unit_contains_tmux_command():
    unit = render_systemd_unit({
        "server_dir": "/opt/fivem/server",
        "server_cfg": "server.cfg",
        "service_name": "fivem",
        "run_user": "fivem",
        "console_mode": "tmux",
    })

    assert "User=fivem" in unit
    assert "WorkingDirectory=/opt/fivem/server" in unit
    assert "tmux new-session -d -s fivem" in unit
    assert "/opt/fivem/server/run.sh +exec server.cfg" in unit
    assert "FiveM exited with status" in unit
    assert "exec /bin/sh" in unit


def test_render_systemd_unit_quotes_config_with_spaces():
    unit = render_systemd_unit({
        "server_dir": "/opt/fivem/server",
        "server_cfg": "configs/live server.cfg",
        "service_name": "fivem",
        "run_user": "neo",
        "console_mode": "tmux",
    })

    assert "/opt/fivem/server/run.sh +exec" in unit
    assert "live server.cfg" in unit


def test_render_systemd_unit_uses_absolute_config_path_outside_server_dir():
    unit = render_systemd_unit({
        "server_dir": "/opt/fivem/server",
        "server_cfg": "/etc/fivem/configs/production.cfg",
        "service_name": "fivem",
        "run_user": "neo",
        "console_mode": "tmux",
    })

    assert "WorkingDirectory=/etc/fivem/configs" in unit
    assert "/opt/fivem/server/run.sh +exec production.cfg" in unit


def test_render_systemd_unit_combines_config_dir_and_filename():
    unit = render_systemd_unit({
        "server_dir": "/opt/fivem/server",
        "server_cfg_dir": "/etc/fivem/configs",
        "server_cfg_file": "city.cfg",
        "service_name": "fivem",
        "run_user": "neo",
        "console_mode": "tmux",
    })

    assert "WorkingDirectory=/etc/fivem/configs" in unit
    assert "/opt/fivem/server/run.sh +exec city.cfg" in unit


def test_render_systemd_unit_runs_from_relative_config_directory():
    unit = render_systemd_unit({
        "server_dir": "/opt/fivem/server",
        "server_cfg_dir": "server-data/dev",
        "server_cfg_file": "server.dev.cfg",
        "service_name": "fivem-dev",
        "run_user": "neo",
        "console_mode": "tmux",
    })

    assert "WorkingDirectory=/opt/fivem/server/server-data/dev" in unit
    assert "/opt/fivem/server/run.sh +exec server.dev.cfg" in unit


def test_invalid_service_name_rejected():
    with pytest.raises(ValueError):
        validate_service_name("five;m")
