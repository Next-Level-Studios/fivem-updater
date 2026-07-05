import os
from pathlib import Path

SYSTEM_CONFIG_PATH = Path("/etc/updatefivem/config.json")
SYSTEM_CACHE_DIR = Path("/var/cache/updatefivem")
LOG_PATH = Path("/var/log/updatefivem.log")


def _xdg_path(env_name: str, fallback: Path, *parts: str) -> Path:
    base = Path(os.environ.get(env_name) or fallback)
    return base.joinpath(*parts)


def user_config_path() -> Path:
    return _xdg_path("XDG_CONFIG_HOME", Path.home() / ".config", "updatefivem", "config.json")


def user_cache_dir() -> Path:
    return _xdg_path("XDG_CACHE_HOME", Path.home() / ".cache", "updatefivem")


def config_path() -> Path:
    return Path(os.environ.get("UPDATEFIVEM_CONFIG_PATH") or user_config_path())


def cache_dir() -> Path:
    return Path(os.environ.get("UPDATEFIVEM_CACHE_DIR") or user_cache_dir())
