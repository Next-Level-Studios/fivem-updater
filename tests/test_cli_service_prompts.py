import pytest
import typer

from updatefivem import cli


def test_prepare_service_for_update_stops_after_confirmation(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.Confirm, "ask", lambda *args, **kwargs: True)
    monkeypatch.setattr(cli, "_run_service_action", lambda action, service_name: calls.append((action, service_name)))

    stopped = cli._prepare_service_for_update({"service_name": "fivem-dev"}, assume_yes=False, service_control=True)

    assert stopped is True
    assert calls == [("stop", "fivem-dev")]


def test_prepare_service_for_update_aborts_when_not_ready(monkeypatch):
    monkeypatch.setattr(cli.Confirm, "ask", lambda *args, **kwargs: False)

    with pytest.raises(typer.Exit):
        cli._prepare_service_for_update({"service_name": "fivem-dev"}, assume_yes=False, service_control=True)


def test_prepare_service_for_update_can_be_skipped(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "_run_service_action", lambda action, service_name: calls.append((action, service_name)))

    stopped = cli._prepare_service_for_update({"service_name": "fivem-dev"}, assume_yes=False, service_control=False)

    assert stopped is False
    assert calls == []


def test_offer_start_after_update_starts_after_confirmation(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.Confirm, "ask", lambda *args, **kwargs: True)
    monkeypatch.setattr(cli, "_run_service_action", lambda action, service_name: calls.append((action, service_name)))

    cli._offer_start_after_update({"service_name": "fivem-dev"}, assume_yes=False, service_was_stopped=True)

    assert calls == [("start", "fivem-dev")]


def test_offer_start_after_update_does_nothing_if_service_was_not_stopped(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "_run_service_action", lambda action, service_name: calls.append((action, service_name)))

    cli._offer_start_after_update({"service_name": "fivem-dev"}, assume_yes=True, service_was_stopped=False)

    assert calls == []
