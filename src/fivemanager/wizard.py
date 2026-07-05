from __future__ import annotations

from pathlib import Path

from rich.panel import Panel

from .config import add_server, default_config, next_ports, save_config, slugify, validate_runtime_dir
from .paths import OLD_CONFIG_PATH, config_path
from .txadmin import write_txadmin_profile
from .ui import console, info, success, warn


def _inquirer():
    try:
        from InquirerPy import inquirer
        return inquirer
    except Exception:
        return None


def ask_text(message: str, default: str | None = None) -> str:
    iq = _inquirer()
    if iq:
        return iq.text(message=message, default=default or "").execute().strip()
    prompt = f"{message}"
    if default:
        prompt += f" ({default})"
    value = input(prompt + ": ").strip()
    return value or (default or "")


def ask_confirm(message: str, default: bool = True) -> bool:
    iq = _inquirer()
    if iq:
        return bool(iq.confirm(message=message, default=default).execute())
    suffix = "Y/n" if default else "y/N"
    value = input(f"{message} [{suffix}]: ").strip().lower()
    if not value:
        return default
    return value.startswith("y")


def ask_select(message: str, choices: list[tuple[str, str]] | list[str]) -> str:
    iq = _inquirer()
    if iq:
        formatted = [{"name": c[0], "value": c[1]} if isinstance(c, tuple) else c for c in choices]
        return iq.select(message=message, choices=formatted).execute()
    for idx, choice in enumerate(choices, 1):
        label = choice[0] if isinstance(choice, tuple) else choice
        print(f"{idx}. {label}")
    while True:
        raw = input(f"{message}: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            choice = choices[int(raw) - 1]
            return choice[1] if isinstance(choice, tuple) else choice


def ask_checkbox(message: str, choices: list[tuple[str, int]]) -> list[int]:
    iq = _inquirer()
    if iq:
        return list(iq.checkbox(message=message, choices=[{"name": n, "value": v} for n, v in choices]).execute())
    print(message)
    for idx, (name, _value) in enumerate(choices, 1):
        print(f"{idx}. {name}")
    raw = input("Enter numbers separated by commas, or blank for none: ").strip()
    selected = []
    for part in raw.split(','):
        part = part.strip()
        if part.isdigit() and 1 <= int(part) <= len(choices):
            selected.append(choices[int(part) - 1][1])
    return selected


def ask_runtime_dir() -> Path:
    while True:
        value = ask_text("FiveM runtime directory (where run.sh and alpine/ live)")
        path = Path(value).expanduser()
        errors = validate_runtime_dir(path)
        if not errors:
            return path
        for error in errors:
            warn(error)


def run_setup_wizard(update_callback=None, start_callback=None) -> dict:
    console.print(Panel.fit("[bold cyan]FiveManager setup[/]\nModern-ish server wrangling. Fewer goblins, ideally."))
    if OLD_CONFIG_PATH.exists() and not config_path().exists():
        warn(f"Old updatefivem config found at {OLD_CONFIG_PATH}")
        warn(f"FiveManager starts clean and will save new config at {config_path()}")
    mode = ask_select("Do you want the full FiveM server manager experience, or just the runtime updater?", [
        ("Runtime updater only", "runtime"),
        ("Full server manager", "manager"),
    ])
    runtime = ask_runtime_dir()
    config = default_config()
    config["mode"] = mode
    config["runtime_dir"] = str(runtime)

    if mode == "runtime":
        save_config(config)
        success("Runtime updater configuration saved")
        if ask_confirm("Do you want to update the runtime now?", default=False):
            warn("Updating the runtime while servers are running may break or interrupt currently running servers.")
            if update_callback:
                update_callback(config, force=True)
        else:
            info("Run FiveManager when you are ready to update the server runtime.")
        return config

    while True:
        txa, fxs = next_ports(config)
        name = ask_text("Server name")
        key = ask_text("Internal server key", default=slugify(name))
        data_path = ask_text("Server data path (where this server's resources/ folder lives)")
        cfg_path = ask_text("Server config path (full path to server.cfg)")
        txa_port = int(ask_text("txAdmin port", default=str(txa)))
        fxs_port = int(ask_text("FXServer port", default=str(fxs)))
        interface = ask_text("Interface/bind address", default="0.0.0.0")
        server = add_server(config, name=name, key=key, data_path=data_path, cfg_path=cfg_path, txadmin_port=txa_port, fxserver_port=fxs_port, interface=interface)
        profile = write_txadmin_profile(runtime, server)
        success(f"Created txAdmin profile: {profile}")
        if ask_select("What next?", [("Add another server", "add"), ("Complete setup", "done")]) == "done":
            break
    save_config(config)
    ids = ask_checkbox("Which servers would you like to run now?", [(f"{s['id']} | {s['name']}", int(s['id'])) for s in config.get('servers', [])])
    if start_callback:
        for sid in ids:
            start_callback(config, sid)
    return config
