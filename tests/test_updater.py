import pytest

from updatefivem.updater import build_pip_upgrade_command, find_wheel_asset


def test_find_wheel_asset_prefers_updatefivem_wheel():
    release = {
        "tag_name": "v0.1.3",
        "assets": [
            {"name": "notes.txt", "browser_download_url": "https://example.test/notes.txt"},
            {"name": "updatefivem-0.1.3-py3-none-any.whl", "browser_download_url": "https://example.test/updatefivem.whl"},
        ],
    }

    asset = find_wheel_asset(release)

    assert asset["name"] == "updatefivem-0.1.3-py3-none-any.whl"
    assert asset["browser_download_url"] == "https://example.test/updatefivem.whl"


def test_find_wheel_asset_raises_without_wheel():
    with pytest.raises(RuntimeError, match="wheel"):
        find_wheel_asset({"assets": [{"name": "source.tar.gz"}]})


def test_build_pip_upgrade_command_uses_current_python():
    cmd = build_pip_upgrade_command("https://example.test/updatefivem.whl", python_executable="/opt/updatefivem/venv/bin/python")

    assert cmd == [
        "/opt/updatefivem/venv/bin/python",
        "-m",
        "pip",
        "install",
        "--upgrade",
        "https://example.test/updatefivem.whl",
    ]
