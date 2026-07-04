from pathlib import Path

from updatefivem.config import default_run_user, load_config, save_config, validate_config
from updatefivem.paths import cache_dir, config_path


def test_env_overrides_paths(monkeypatch, tmp_path):
    cfg = tmp_path / "config.json"
    cache = tmp_path / "cache"
    monkeypatch.setenv("UPDATEFIVEM_CONFIG_PATH", str(cfg))
    monkeypatch.setenv("UPDATEFIVEM_CACHE_DIR", str(cache))

    assert config_path() == cfg
    assert cache_dir() == cache


def test_missing_config_returns_none(monkeypatch, tmp_path):
    monkeypatch.setenv("UPDATEFIVEM_CONFIG_PATH", str(tmp_path / "missing.json"))
    assert load_config() is None


def test_save_and_load_config(monkeypatch, tmp_path):
    cfg_path = tmp_path / "nested" / "config.json"
    monkeypatch.setenv("UPDATEFIVEM_CONFIG_PATH", str(cfg_path))
    config = {
        "server_dir": str(tmp_path),
        "server_cfg": "server.cfg",
        "service_name": "fivem",
        "run_user": "neo",
        "console_mode": "tmux",
    }

    save_config(config)

    assert cfg_path.exists()
    assert load_config() == config


def test_validate_config_requires_server_dir(tmp_path):
    errors = validate_config({"server_cfg": "server.cfg", "service_name": "fivem"})
    assert any("server_dir" in error for error in errors)


def test_validate_config_accepts_relative_server_cfg(tmp_path):
    errors = validate_config({
        "server_dir": str(tmp_path),
        "server_cfg": "configs/live.cfg",
        "service_name": "fivem",
        "run_user": "neo",
        "console_mode": "tmux",
    })
    assert errors == []


def test_default_run_user_is_non_empty():
    assert default_run_user()
