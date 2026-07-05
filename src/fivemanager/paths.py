from __future__ import annotations

import os
from pathlib import Path

OLD_CONFIG_PATH = Path.home() / ".config" / "updatefivem" / "config.json"


def _xdg_path(env_name: str, fallback: Path) -> Path:
    value = os.environ.get(env_name)
    return Path(value).expanduser() if value else fallback


def config_path() -> Path:
    override = os.environ.get("FIVEMANAGER_CONFIG_PATH")
    if override:
        return Path(override).expanduser()
    base = _xdg_path("XDG_CONFIG_HOME", Path.home() / ".config")
    return base / "fivemanager" / "config.json"


def cache_dir() -> Path:
    override = os.environ.get("FIVEMANAGER_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    base = _xdg_path("XDG_CACHE_HOME", Path.home() / ".cache")
    return base / "fivemanager"
