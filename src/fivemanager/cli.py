from __future__ import annotations

import shutil
import sys
from pathlib import Path

import typer
from rich.table import Table

from . import __version__
from .artifacts import download_artifact, selected_artifact
from .backup import create_backup, list_backups, restore_backup
from .config import get_server, load_config, remove_server as remove_server_config, require_config, runtime_dir, save_config
from .installer import install_archive
from .paths import cache_dir
from .tmux import attach_console, format_bytes, memory_bytes_for_session, restart_server, session_exists, session_name, start_server, stop_server
from .txadmin import write_txadmin_profile
from .ui import console, error, info, success, warn
from .updater import run_self_update
from .wizard import ask_confirm, ask_select, run_setup_wizard

app = typer.Typer(help="FiveManager — FiveM runtime updater and tmux-based server manager.", no_args_is_help=False)


def _alias_notice() -> None:
    if Path(sys.argv[0]).name == "updatefivem":
        warn("updatefivem has been renamed to fivemanager. This alias will remain during the transition.")


def _update_runtime(config: dict, *, force: bool = False, artifact: str | None = None) -> None:
    runtime = runtime_dir(config)
    if config.get("mode") == "manager" and not force:
        running = [s for s in config.get("servers", []) if session_exists(session_name(s))]
        if running:
            choice = ask_select(
                "Managed servers are running. What should FiveManager do before updating the runtime?",
                [
                    ("Stop running managed servers and update", "stop"),
                    ("Update anyway", "anyway"),
                    ("Cancel", "cancel"),
                ],
            )
            if choice == "cancel":
                warn("Runtime update cancelled.")
                return
            if choice == "stop":
                for server in running:
                    stop_server(server)
    backup = create_backup(runtime)
    success(f"Created backup: {backup}")
    artifact_obj = selected_artifact(artifact)
    archive = download_artifact(artifact_obj, cache_dir())
    install_archive(archive, cache_dir(), runtime)
    success(f"Installed FiveM artifact {artifact_obj.build} into {runtime}")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    artifact: str | None = typer.Option(None, "--artifact", help="Explicit artifact build or .tar.xz URL for runtime update."),
):
    _alias_notice()
    if ctx.invoked_subcommand is not None:
        return
    config = load_config()
    if not config:
        run_setup_wizard(update_callback=lambda cfg, force=False: _update_runtime(cfg, force=force, artifact=artifact), start_callback=start_server_by_id)
        return
    if config.get("mode") == "runtime":
        _update_runtime(config, force=True, artifact=artifact)
        return
    console.print("[bold cyan]FiveManager[/] is configured in full manager mode.")
    console.print("Use [bold]fivemanager status[/], [bold]fivemanager start <id>[/], or [bold]fivemanager update-runtime[/].")


@app.command("setup")
def setup_command():
    """Run the interactive setup wizard again."""
    run_setup_wizard(update_callback=lambda cfg, force=False: _update_runtime(cfg, force=force), start_callback=start_server_by_id)


@app.command("update-runtime")
def update_runtime_command(artifact: str | None = typer.Option(None, "--artifact")):
    """Backup and update the shared FiveM runtime."""
    _update_runtime(require_config(), artifact=artifact)


@app.command("restore")
def restore_command():
    """Restore alpine/, txData/, and run.sh from a runtime backup."""
    config = require_config()
    runtime = runtime_dir(config)
    backups = list_backups(runtime)
    if not backups:
        warn("No backups found.")
        return
    choices = [(f"{idx}. {path.name}", str(idx)) for idx, path in enumerate(backups, 1)] + [("cancel", "cancel")]
    choice = ask_select("Select a backup to restore", choices)
    if choice == "cancel":
        return
    selected = backups[int(choice) - 1]
    warn("Current alpine/, txData/, and run.sh will be replaced.")
    if not ask_confirm(f"Restore backup {selected.name}?", default=False):
        warn("Restore cancelled.")
        return
    restore_backup(runtime, selected)
    success(f"Restored backup: {selected}")


def start_server_by_id(config: dict, server_id: int) -> None:
    server = get_server(config, server_id)
    write_txadmin_profile(runtime_dir(config), server)
    name = start_server(runtime_dir(config), server)
    success(f"Started {server['name']} in tmux session {name}")


@app.command("start")
def start_command(server_id: int):
    start_server_by_id(require_config(), server_id)


@app.command("stop")
def stop_command(server_id: int):
    server = get_server(require_config(), server_id)
    stop_server(server)
    success(f"Stopped {server['name']}")


@app.command("restart")
def restart_command(server_id: int):
    config = require_config()
    server = get_server(config, server_id)
    write_txadmin_profile(runtime_dir(config), server)
    name = restart_server(runtime_dir(config), server)
    success(f"Restarted {server['name']} in tmux session {name}")


@app.command("console")
def console_command(server_id: int):
    server = get_server(require_config(), server_id)
    console.print("Detach without stopping the server: Ctrl+B, then D")
    attach_console(server)


@app.command("status")
def status_command():
    config = require_config()
    table = Table(title="FiveManager servers")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Server name", style="bold")
    table.add_column("Active status")
    table.add_column("Memory usage", justify="right")
    for server in sorted(config.get("servers", []), key=lambda s: int(s["id"])):
        name = session_name(server)
        active = session_exists(name)
        table.add_row(str(server["id"]), server["name"], "[green]running[/]" if active else "[red]stopped[/]", format_bytes(memory_bytes_for_session(name)) if active else "-")
    console.print(table)


@app.command("remove")
def remove_command(server_id: int):
    config = require_config()
    server = get_server(config, server_id)
    warn(f"This will remove {server['name']} from FiveManager and stop its tmux session if present.")
    if not ask_confirm("Continue?", default=False):
        return
    stop_server(server)
    removed = remove_server_config(config, server_id)
    txdata = runtime_dir(config) / "txData" / removed["key"]
    if ask_confirm(f"Also delete txData directory {txdata}?", default=False):
        if txdata.exists():
            shutil.rmtree(txdata)
            success(f"Deleted {txdata}")
    else:
        info(f"Server data path still exists: {removed['data_path']}")
        info(f"txData path still exists: {txdata}")
    save_config(config)
    success(f"Removed server {removed['name']}")


@app.command("self-update")
def self_update(
    dry_run: bool = typer.Option(False, "--dry-run"),
    prerelease: bool = typer.Option(False, "--prerelease", help="Include prerelease alpha/beta builds."),
):
    try:
        tag, name, url, cmd = run_self_update(dry_run=dry_run, include_prereleases=prerelease)
    except RuntimeError as exc:
        warn(str(exc))
        if not prerelease:
            info("Use --prerelease to opt into alpha/beta builds, or install a specific release wheel manually.")
        raise typer.Exit(0)
    info(f"Latest FiveManager release: {tag}")
    info(f"Wheel: {name}")
    if dry_run:
        console.print(" ".join(cmd))
    else:
        success(f"Updated FiveManager from {url}")


def run():
    app()
