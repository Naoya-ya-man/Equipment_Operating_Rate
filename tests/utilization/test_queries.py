from datetime import datetime
from unittest.mock import MagicMock

from src.utilization.queries import fetch_range_aggregates


def test_fetch_range_aggregates_builds_dict_keyed_by_machine_and_unit():
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = [
        ("A", "1", 1200, 1),
        ("A", "2", 2400, 2),
    ]

    result = fetch_range_aggregates(connection, datetime(2026, 7, 7), datetime(2026, 7, 8))

    assert result == {("A", 1): (1200, 1), ("A", 2): (2400, 2)}
    connection.cursor.return_value.execute.assert_called_once()


def test_fetch_range_aggregates_handles_null_aggregates():
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = [("C", "3", None, None)]

    result = fetch_range_aggregates(connection, datetime(2026, 7, 7), datetime(2026, 7, 8))

    assert result == {("C", 3): (0, 0)}
