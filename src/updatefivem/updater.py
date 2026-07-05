from __future__ import annotations

import subprocess
import sys
from typing import Any

import requests

GITHUB_LATEST_RELEASE_API = "https://api.github.com/repos/Next-Level-Studios/fivem-updater/releases/latest"


def fetch_latest_release(api_url: str = GITHUB_LATEST_RELEASE_API) -> dict[str, Any]:
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    return response.json()


def find_wheel_asset(release: dict[str, Any]) -> dict[str, Any]:
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if name.startswith("updatefivem-") and name.endswith(".whl") and asset.get("browser_download_url"):
            return asset
    raise RuntimeError("Latest release does not contain an updatefivem wheel asset")


def build_pip_upgrade_command(url: str, python_executable: str | None = None) -> list[str]:
    return [python_executable or sys.executable, "-m", "pip", "install", "--upgrade", url]


def latest_wheel_info() -> tuple[str, str, str]:
    release = fetch_latest_release()
    asset = find_wheel_asset(release)
    tag = release.get("tag_name", "latest")
    name = asset.get("name", "updatefivem.whl")
    url = asset["browser_download_url"]
    return tag, name, url


def run_self_update(dry_run: bool = False) -> tuple[str, str, str, list[str]]:
    tag, name, url = latest_wheel_info()
    cmd = build_pip_upgrade_command(url)
    if not dry_run:
        subprocess.run(cmd, check=True)
    return tag, name, url, cmd
