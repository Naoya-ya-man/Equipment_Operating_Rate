from datetime import datetime
from unittest.mock import MagicMock

from src.db_loader.merge import merge_records
from src.db_loader.models import DbRecord


def _make_record(product_number: str = "185001A", machine_number: str = "1") -> DbRecord:
    return DbRecord(
        product_number=product_number,
        machine_name="A",
        machine_number=machine_number,
        processing_start_time=datetime(2026, 7, 4, 8, 0, 0),
        processing_completion_time=datetime(2026, 7, 4, 8, 20, 0),
        sum_datetime=1200,
        pass_judgment="OK",
    )


def test_merge_records_executes_once_per_record():
    connection = MagicMock()
    records = [_make_record("185001A"), _make_record("185002B")]

    result_count = merge_records(connection, records)

    assert result_count == 2
    assert connection.cursor.return_value.execute.call_count == 2


def test_merge_records_passes_product_and_machine_number_for_match_condition():
    connection = MagicMock()
    record = _make_record(product_number="185001A", machine_number="3")

    merge_records(connection, [record])

    call_args = connection.cursor.return_value.execute.call_args
    sql, *params = call_args[0]
    assert "MERGE" in sql
    # USING句のマッチキー(先頭2パラメータ)がProduct_Number, Machine_Numberであること(BR-5)
    assert params[0] == "185001A"
    assert params[1] == "3"


def test_merge_records_returns_zero_for_empty_list():
    connection = MagicMock()
    assert merge_records(connection, []) == 0
    connection.cursor.return_value.execute.assert_not_called()
