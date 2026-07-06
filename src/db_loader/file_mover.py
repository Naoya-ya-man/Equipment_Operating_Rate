"""取り込み結果に応じたファイル移動(BR-6)。"""
from __future__ import annotations

import shutil
from pathlib import Path


def move_to_success(csv_path: Path, success_dir: Path) -> Path:
    return _move(csv_path, success_dir)


def move_to_error(csv_path: Path, error_dir: Path) -> Path:
    return _move(csv_path, error_dir)


def _move(csv_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / csv_path.name
    shutil.move(str(csv_path), str(destination))
    return destination
