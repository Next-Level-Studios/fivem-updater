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


def _combine_cfg_parts(server_cfg_dir: str | None, server_cfg_file: str | None) -> str | None:
    if server_cfg_dir and server_cfg_file:
        return str(Path(server_cfg_dir) / server_cfg_file)
    if server_cfg_file:
        return server_cfg_file
    return None


def resolve_server_cfg(config: dict) -> Path:
    server_dir = Path(config.get("server_dir") or ".")
    combined = _combine_cfg_parts(config.get("server_cfg_dir"), config.get("server_cfg_file"))
    cfg_value = combined or config.get("server_cfg") or "server.cfg"
    cfg_path = Path(cfg_value)
    if cfg_path.is_absolute():
        return cfg_path
    return server_dir / cfg_path


def server_working_dir(config: dict) -> Path:
    return resolve_server_cfg(config).parent


def server_cfg_exec_arg(config: dict) -> str:
    """Return the value passed to `+exec`.

    The service runs from the directory containing the chosen cfg, so nested
    `exec other.cfg` lines inside server.cfg resolve beside that cfg rather than
    beside the artifact runtime directory.
    """
    return resolve_server_cfg(config).name


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []
    server_dir = config.get("server_dir")
    if not server_dir:
        errors.append("server_dir is required")
    elif not Path(server_dir).exists():
        errors.append(f"server_dir does not exist: {server_dir}")

    if not server_cfg_exec_arg(config):
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

    combined = _combine_cfg_parts(config.get("server_cfg_dir"), config.get("server_cfg_file"))
    if combined:
        config["server_cfg"] = combined
    return config
