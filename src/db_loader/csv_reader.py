"""CSV読み込み・型変換(BR-4)。"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .config import CSV_COLUMNS, DATETIME_FORMAT
from .models import DbRecord


def read_csv_records(csv_path: Path) -> list[DbRecord]:
    """CSVを読み込み、SSMSのカラム型に合わせて変換したDbRecordのリストを返す。"""
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != CSV_COLUMNS:
            raise ValueError(f"CSVのカラム構成が不正です: {reader.fieldnames}")

        return [_to_db_record(row) for row in reader]


def _to_db_record(row: dict[str, str]) -> DbRecord:
    return DbRecord(
        product_number=row["Product_Number"],
        machine_name=row["Machine_Name"],
        machine_number=str(row["Machine_Number"]),
        processing_start_time=datetime.strptime(row["Processing_Start_Time"], DATETIME_FORMAT),
        processing_completion_time=datetime.strptime(row["Processing_Completion_Time"], DATETIME_FORMAT),
        sum_datetime=int(row["Sum_DateTime"]),
        pass_judgment=row["Pass_judgment"],
    )
