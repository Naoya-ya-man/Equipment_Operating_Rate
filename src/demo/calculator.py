"""ポートフォリオデモ用の稼働率算出(SQLiteバックエンド)。

`src.utilization.calculator`と同じ関数シグネチャ・戻り値の型を提供する。
号機→加工機タイプへの集計ロジック(`aggregate_by_machine_type`等)は、
データ取得後の純粋な計算であり実DBに依存しないため、本番のものをそのまま再利用する。
データ取得部分のみ、SQL Server(pyodbc)ではなくSQLiteに対して問い合わせる
(T-SQLとSQLiteで日時パラメータの扱いが異なるため、クエリ層は独自実装としている)。
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta

from src.utilization.calculator import (  # noqa: F401 - デモ側でも同じ集計ロジックを再利用する
    aggregate_by_machine_type,
    aggregate_weekly_by_machine_type,
)
from src.utilization.config import MACHINE_TYPES, STANDARD_MINUTES, UNIT_NUMBERS
from src.utilization.models import UtilizationRow, WeeklyUtilizationRow
from src.utilization.planned_time import get_planned_seconds

from .generate_demo_data import DEMO_DB_PATH, TABLE_NAME

MONDAY_WEEKDAY = 0

_QUERY_SQL = f"""
SELECT Machine_Name, Machine_Number, SUM(Sum_DateTime) AS actual_seconds, COUNT(*) AS processed_count
FROM {TABLE_NAME}
WHERE Processing_Start_Time >= ? AND Processing_Start_Time < ?
GROUP BY Machine_Name, Machine_Number
""".strip()


def get_latest_data_date() -> date:
    """デモDBに含まれる最新のデータ日付を返す。

    デモは静的な事前生成データのため、カレンダー上の「今日」を基準に表示すると
    データ生成日以降は空白になってしまう。そのため、表示の基準日には実際の
    カレンダー日ではなくこの値を使う(常にデータがある状態で表示するため)。
    """
    connection = sqlite3.connect(DEMO_DB_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT MAX(Processing_Start_Time) FROM {TABLE_NAME}")
        result = cursor.fetchone()[0]
        if result is None:
            return date.today()
        return datetime.fromisoformat(result).date()
    finally:
        connection.close()


def get_daily_utilization(target_date: date) -> list[UtilizationRow]:
    """対象日の号機別(25件)日別稼働率(実績+想定)を算出する。"""
    planned_seconds = get_planned_seconds(target_date)
    aggregates = _fetch_aggregates(target_date, target_date + timedelta(days=1))
    return _build_utilization_rows(aggregates, planned_seconds)


def get_weekly_utilization(week_start: date) -> list[WeeklyUtilizationRow]:
    """月曜始まりの週について、号機別(25件)週間稼働率・週間想定稼働率を算出する。"""
    if week_start.weekday() != MONDAY_WEEKDAY:
        raise ValueError("week_startは月曜日の日付を指定してください")

    week_end = week_start + timedelta(days=7)
    total_planned = sum(get_planned_seconds(week_start + timedelta(days=i)) for i in range(7))
    aggregates = _fetch_aggregates(week_start, week_end)

    rows = []
    for machine_name in MACHINE_TYPES:
        standard_seconds = STANDARD_MINUTES[machine_name] * 60
        for unit_number in UNIT_NUMBERS:
            actual_seconds, processed_count = aggregates.get((machine_name, unit_number), (0, 0))
            expected_seconds = processed_count * standard_seconds
            rows.append(
                WeeklyUtilizationRow(
                    machine_name=machine_name,
                    machine_number=unit_number,
                    actual_seconds=actual_seconds,
                    planned_seconds=total_planned,
                    processed_count=processed_count,
                    actual_utilization_rate=_safe_rate(actual_seconds, total_planned),
                    expected_utilization_rate=_safe_rate(expected_seconds, total_planned),
                )
            )
    return rows


def get_monthly_utilization(year: int, month: int) -> list[UtilizationRow]:
    """対象月の号機別(25件)月別稼働率(実績+想定)を算出する。日別集計を月内で積み上げる。"""
    days_in_month = _days_in_month(year, month)
    totals: dict[tuple[str, int], list[int]] = {(m, u): [0, 0, 0] for m in MACHINE_TYPES for u in UNIT_NUMBERS}

    for day_offset in range(days_in_month):
        target_date = date(year, month, 1) + timedelta(days=day_offset)
        for row in get_daily_utilization(target_date):
            key = (row.machine_name, row.machine_number)
            totals[key][0] += row.actual_seconds
            totals[key][1] += row.planned_seconds
            totals[key][2] += row.processed_count

    rows = []
    for (machine_name, unit_number), (actual_seconds, planned_seconds, processed_count) in totals.items():
        expected_seconds = processed_count * STANDARD_MINUTES[machine_name] * 60
        rows.append(
            UtilizationRow(
                machine_name=machine_name,
                machine_number=unit_number,
                actual_seconds=actual_seconds,
                planned_seconds=planned_seconds,
                utilization_rate=_safe_rate(actual_seconds, planned_seconds),
                processed_count=processed_count,
                expected_utilization_rate=_safe_rate(expected_seconds, planned_seconds),
            )
        )
    return rows


def _build_utilization_rows(
    aggregates: dict[tuple[str, int], tuple[int, int]], planned_seconds: int
) -> list[UtilizationRow]:
    rows = []
    for machine_name in MACHINE_TYPES:
        standard_seconds = STANDARD_MINUTES[machine_name] * 60
        for unit_number in UNIT_NUMBERS:
            actual_seconds, processed_count = aggregates.get((machine_name, unit_number), (0, 0))
            expected_seconds = processed_count * standard_seconds
            rows.append(
                UtilizationRow(
                    machine_name=machine_name,
                    machine_number=unit_number,
                    actual_seconds=actual_seconds,
                    planned_seconds=planned_seconds,
                    utilization_rate=_safe_rate(actual_seconds, planned_seconds),
                    processed_count=processed_count,
                    expected_utilization_rate=_safe_rate(expected_seconds, planned_seconds),
                )
            )
    return rows


def _fetch_aggregates(range_start: date, range_end: date) -> dict[tuple[str, int], tuple[int, int]]:
    start_str = datetime.combine(range_start, datetime.min.time()).isoformat(sep=" ")
    end_str = datetime.combine(range_end, datetime.min.time()).isoformat(sep=" ")

    connection = sqlite3.connect(DEMO_DB_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(_QUERY_SQL, (start_str, end_str))
        aggregates: dict[tuple[str, int], tuple[int, int]] = {}
        for machine_name, machine_number, actual_seconds, processed_count in cursor.fetchall():
            aggregates[(machine_name, int(machine_number))] = (int(actual_seconds or 0), int(processed_count or 0))
        return aggregates
    finally:
        connection.close()


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator * 100, 2)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    return (next_month_first - date(year, month, 1)).days
