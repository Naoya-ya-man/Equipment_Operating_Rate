from datetime import datetime

import pytest

from src.db_loader.csv_reader import read_csv_records

HEADER = "Product_Number,Machine_Name,Machine_Number,Processing_Start_Time,Processing_Completion_Time,Sum_DateTime,Pass_judgment\n"


def test_read_csv_records_converts_types_correctly(tmp_path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        HEADER + "185001A,A,3,2026-07-04 08:00:00,2026-07-04 08:20:00,1200,OK\n",
        encoding="utf-8",
    )

    records = read_csv_records(csv_path)

    assert len(records) == 1
    record = records[0]
    assert record.product_number == "185001A"
    assert record.machine_name == "A"
    assert record.machine_number == "3"  # int -> str変換(BR-4)
    assert record.processing_start_time == datetime(2026, 7, 4, 8, 0, 0)
    assert record.processing_completion_time == datetime(2026, 7, 4, 8, 20, 0)
    assert record.sum_datetime == 1200
    assert record.pass_judgment == "OK"


def test_read_csv_records_raises_on_unexpected_columns(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("Foo,Bar\n1,2\n", encoding="utf-8")

    with pytest.raises(ValueError):
        read_csv_records(csv_path)


def test_read_csv_records_handles_empty_body(tmp_path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text(HEADER, encoding="utf-8")

    assert read_csv_records(csv_path) == []
