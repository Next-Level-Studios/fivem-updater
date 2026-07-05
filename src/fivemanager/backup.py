from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

BACKUP_ITEMS = ("alpine", "txData", "run.sh")


def backup_root(runtime_dir: Path) -> Path:
    return runtime_dir / "backup"


def list_backups(runtime_dir: Path) -> list[Path]:
    root = backup_root(runtime_dir)
    if not root.exists():
        return []
    return sorted([p for p in root.iterdir() if p.is_dir()], reverse=True)


def prune_backups(runtime_dir: Path, keep: int = 3) -> None:
    for old in list_backups(runtime_dir)[keep:]:
        shutil.rmtree(old)


def create_backup(runtime_dir: Path, keep: int = 3) -> Path:
    root = backup_root(runtime_dir)
    root.mkdir(parents=True, exist_ok=True)
    dest = root / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    suffix = 1
    while dest.exists():
        dest = root / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{suffix}"
        suffix += 1
    dest.mkdir()
    for item in BACKUP_ITEMS:
        src = runtime_dir / item
        if not src.exists() and not src.is_symlink():
            continue
        if src.is_dir() and not src.is_symlink():
            shutil.copytree(src, dest / item, symlinks=True)
        else:
            shutil.copy2(src, dest / item, follow_symlinks=False)
    prune_backups(runtime_dir, keep=keep)
    return dest


def restore_backup(runtime_dir: Path, backup_dir: Path) -> None:
    if not backup_dir.exists():
        raise RuntimeError(f"Backup does not exist: {backup_dir}")
    for item in BACKUP_ITEMS:
        target = runtime_dir / item
        if target.exists() or target.is_symlink():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
    for item in BACKUP_ITEMS:
        src = backup_dir / item
        if not src.exists() and not src.is_symlink():
            continue
        target = runtime_dir / item
        if src.is_dir() and not src.is_symlink():
            shutil.copytree(src, target, symlinks=True)
        else:
            shutil.copy2(src, target, follow_symlinks=False)
