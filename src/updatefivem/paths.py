import os
from pathlib import Path

SYSTEM_CONFIG_PATH = Path("/etc/updatefivem/config.json")
SYSTEM_CACHE_DIR = Path("/var/cache/updatefivem")
LOG_PATH = Path("/var/log/updatefivem.log")


def config_path() -> Path:
    return Path(os.environ.get("UPDATEFIVEM_CONFIG_PATH", SYSTEM_CONFIG_PATH))


def cache_dir() -> Path:
    return Path(os.environ.get("UPDATEFIVEM_CACHE_DIR", SYSTEM_CACHE_DIR))
