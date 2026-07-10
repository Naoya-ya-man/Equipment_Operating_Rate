"""ポートフォリオ用デモデータの生成(SQLite)。

`CsvGenerator`のロジックをそのまま流用し、過去N日分の疑似稼働データを生成して
`src/demo/demo_data.db`に保存する。実際のSSMSには一切アクセスしない。
"""
from __future__ import annotations

import sqlite3
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from src.csv_generator.generator import generate_daily_csv
from src.db_loader.csv_reader import read_csv_records

DEMO_DB_PATH = Path(__file__).resolve().parent / "demo_data.db"
TABLE_NAME = "A1_ProcessingMachine_Utilization_Rate"
DEFAULT_NUM_DAYS = 90

_SCHEMA_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    Product_Number TEXT NOT NULL,
    Machine_Name TEXT NOT NULL,
    Machine_Number TEXT NOT NULL,
    Processing_Start_Time TEXT NOT NULL,
    Processing_Completion_Time TEXT NOT NULL,
    Sum_DateTime INTEGER NOT NULL,
    "Pass judgment" TEXT NOT NULL
);
"""

_INSERT_SQL = f"INSERT INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?)"


def generate_demo_database(num_days: int = DEFAULT_NUM_DAYS, end_date: Optional[date] = None) -> Path:
    """直近num_days日分の疑似データを生成し、SQLiteファイル(demo_data.db)に保存する。"""
    end_date = end_date or date.today()
    start_date = end_date - timedelta(days=num_days - 1)

    if DEMO_DB_PATH.exists():
        DEMO_DB_PATH.unlink()

    connection = sqlite3.connect(DEMO_DB_PATH)
    try:
        connection.execute(_SCHEMA_SQL)

        with tempfile.TemporaryDirectory() as tmp:
            workspace_root = Path(tmp)
            current = start_date
            while current <= end_date:
                for hour in (0, 12):
                    reference_time = datetime(current.year, current.month, current.day, hour, 0)
                    csv_path = generate_daily_csv(reference_time=reference_time, workspace_root=workspace_root)
                    if csv_path is None:
                        continue  # 日曜日はCSVが生成されないためスキップ
                    _insert_records(connection, csv_path)
                current += timedelta(days=1)

        connection.commit()
    finally:
        connection.close()

    return DEMO_DB_PATH


def _insert_records(connection: sqlite3.Connection, csv_path: Path) -> None:
    records = read_csv_records(csv_path)
    connection.executemany(
        _INSERT_SQL,
        [
            (
                r.product_number,
                r.machine_name,
                r.machine_number,
                r.processing_start_time.isoformat(sep=" "),
                r.processing_completion_time.isoformat(sep=" "),
                r.sum_datetime,
                r.pass_judgment,
            )
            for r in records
        ],
    )


if __name__ == "__main__":
    generated_path = generate_demo_database()
    print(f"デモ用データベースを生成しました: {generated_path}")
