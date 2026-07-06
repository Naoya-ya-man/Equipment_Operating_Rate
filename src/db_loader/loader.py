"""DbLoaderのエントリーポイント(UOW-2: CSV -> SSMS 取り込み)。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import ERROR_DIR_NAME, INPUT_DIR_NAME, SUCCESS_DIR_NAME
from .connection import get_connection
from .csv_reader import read_csv_records
from .file_mover import move_to_error, move_to_success
from .merge import merge_records
from .models import LoadResult
from .schema_setup import ensure_schema

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


def load_csv_to_db(csv_path: Path, workspace_root: Optional[Path] = None) -> LoadResult:
    """1CSVファイルを読み込み、型変換のうえMERGEで取り込む。成否に応じてファイルを移動する(BR-6)。"""
    root = workspace_root or WORKSPACE_ROOT
    success_dir = root / SUCCESS_DIR_NAME
    error_dir = root / ERROR_DIR_NAME

    try:
        records = read_csv_records(csv_path)
        connection = get_connection()
        try:
            ensure_schema(connection)
            row_count = merge_records(connection, records)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        move_to_success(csv_path, success_dir)
        return LoadResult(file_path=csv_path, success=True, row_count=row_count)

    except Exception as exc:  # noqa: BLE001 - ファイル単位でエラーを吸収し、他ファイルの処理を継続する
        move_to_error(csv_path, error_dir)
        return LoadResult(file_path=csv_path, success=False, row_count=0, error_message=str(exc))


def load_pending_csv_files(workspace_root: Optional[Path] = None) -> list[LoadResult]:
    """データ転送前/配下の全CSVファイルをファイル名昇順で処理する(BR-8)。"""
    root = workspace_root or WORKSPACE_ROOT
    input_dir = root / INPUT_DIR_NAME
    if not input_dir.exists():
        return []

    return [load_csv_to_db(csv_path, workspace_root=root) for csv_path in sorted(input_dir.glob("*.csv"))]


if __name__ == "__main__":
    outcomes = load_pending_csv_files()
    if not outcomes:
        print("対象CSVファイルはありませんでした。")
    for outcome in outcomes:
        status = "OK" if outcome.success else f"ERROR: {outcome.error_message}"
        print(f"{outcome.file_path.name}: {status} ({outcome.row_count} rows)")
