import getpass
import json
import os
from pathlib import Path

from .paths import config_path

DEFAULTS = {
    "server_cfg": "server.cfg",
    "service_name": "fivem",
    "console_mode": "tmux",
}


def default_run_user() -> str:
    if os.geteuid() == 0:
        return "fivem"
    return getpass.getuser() or "fivem"


def load_config() -> dict | None:
    path = config_path()
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_config(config: dict) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")
    tmp_path.replace(path)


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []
    server_dir = config.get("server_dir")
    if not server_dir:
        errors.append("server_dir is required")
    elif not Path(server_dir).exists():
        errors.append(f"server_dir does not exist: {server_dir}")

    if not config.get("server_cfg"):
        errors.append("server_cfg is required")
    if not config.get("service_name"):
        errors.append("service_name is required")
    if config.get("console_mode", "tmux") != "tmux":
        errors.append("only tmux console_mode is currently supported")
    return errors


def merge_config(existing: dict | None, **updates) -> dict:
    config = dict(DEFAULTS)
    config["run_user"] = default_run_user()
    if existing:
        config.update(existing)
    for key, value in updates.items():
        if value is not None:
            config[key] = str(value)
    return config
