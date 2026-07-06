"""SSMSへの集計クエリ(BR-2, BR-4で参照する号機別の実加工時間・件数)。"""
from __future__ import annotations

from datetime import datetime

from .config import TABLE_NAME

QUERY_SQL_TEMPLATE = """
SELECT Machine_Name, Machine_Number, SUM(Sum_DateTime) AS actual_seconds, COUNT(*) AS processed_count
FROM {table}
WHERE Processing_Start_Time >= ? AND Processing_Start_Time < ?
GROUP BY Machine_Name, Machine_Number
""".strip()


def fetch_range_aggregates(
    connection, range_start: datetime, range_end: datetime
) -> dict[tuple[str, int], tuple[int, int]]:
    """[range_start, range_end)内の号機別 実加工時間合計(秒)・加工件数を取得する。"""
    sql = QUERY_SQL_TEMPLATE.format(table=TABLE_NAME)
    cursor = connection.cursor()
    cursor.execute(sql, range_start, range_end)

    aggregates: dict[tuple[str, int], tuple[int, int]] = {}
    for machine_name, machine_number, actual_seconds, processed_count in cursor.fetchall():
        key = (machine_name, int(machine_number))
        aggregates[key] = (int(actual_seconds or 0), int(processed_count or 0))
    return aggregates
