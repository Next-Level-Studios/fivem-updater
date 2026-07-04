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
    assert "./run.sh +exec server.cfg" in unit


def test_render_systemd_unit_quotes_config_with_spaces():
    unit = render_systemd_unit({
        "server_dir": "/opt/fivem/server",
        "server_cfg": "configs/live server.cfg",
        "service_name": "fivem",
        "run_user": "neo",
        "console_mode": "tmux",
    })

    assert "'./run.sh +exec '" not in unit
    assert "configs/live server.cfg" in unit


def test_render_systemd_unit_uses_absolute_config_path_outside_server_dir():
    unit = render_systemd_unit({
        "server_dir": "/opt/fivem/server",
        "server_cfg": "/etc/fivem/configs/production.cfg",
        "service_name": "fivem",
        "run_user": "neo",
        "console_mode": "tmux",
    })

    assert "./run.sh +exec /etc/fivem/configs/production.cfg" in unit


def test_render_systemd_unit_combines_config_dir_and_filename():
    unit = render_systemd_unit({
        "server_dir": "/opt/fivem/server",
        "server_cfg_dir": "/etc/fivem/configs",
        "server_cfg_file": "city.cfg",
        "service_name": "fivem",
        "run_user": "neo",
        "console_mode": "tmux",
    })

    assert "./run.sh +exec /etc/fivem/configs/city.cfg" in unit


def test_invalid_service_name_rejected():
    with pytest.raises(ValueError):
        validate_service_name("five;m")
