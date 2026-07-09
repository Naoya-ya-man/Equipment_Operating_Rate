"""稼働率算出のエントリーポイント(UOW-3: UtilizationCalculator)。"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from .config import MACHINE_TYPES, STANDARD_MINUTES, UNIT_NUMBERS
from .connection import get_connection
from .models import (
    MachineTypeUtilizationRow,
    MachineTypeWeeklyUtilizationRow,
    UtilizationRow,
    WeeklyUtilizationRow,
)
from .planned_time import get_planned_seconds
from .queries import fetch_range_aggregates

MONDAY_WEEKDAY = 0


def get_daily_utilization(target_date: date, connection=None) -> list[UtilizationRow]:
    """対象日の号機別(25件)日別稼働率(実績+想定)を算出する(BR-2)。"""
    planned_seconds = get_planned_seconds(target_date)
    aggregates = _fetch_aggregates_for_range(target_date, target_date + timedelta(days=1), connection)

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


def get_weekly_utilization(week_start: date, connection=None) -> list[WeeklyUtilizationRow]:
    """月曜始まりの週(BR-3)について、号機別(25件)週間稼働率・週間想定稼働率を算出する(BR-4, BR-5)。"""
    if week_start.weekday() != MONDAY_WEEKDAY:
        raise ValueError("week_startは月曜日の日付を指定してください")

    week_end = week_start + timedelta(days=7)
    total_planned = sum(get_planned_seconds(week_start + timedelta(days=i)) for i in range(7))
    aggregates = _fetch_aggregates_for_range(week_start, week_end, connection)

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


def get_monthly_utilization(year: int, month: int, connection=None) -> list[UtilizationRow]:
    """対象月の号機別(25件)月別稼働率(実績+想定)を算出する(BR-6)。日別集計を月内で積み上げる。"""
    days_in_month = _days_in_month(year, month)
    totals: dict[tuple[str, int], list[int]] = {(m, u): [0, 0, 0] for m in MACHINE_TYPES for u in UNIT_NUMBERS}

    own_connection = connection or get_connection()
    try:
        for day_offset in range(days_in_month):
            target_date = date(year, month, 1) + timedelta(days=day_offset)
            for row in get_daily_utilization(target_date, connection=own_connection):
                key = (row.machine_name, row.machine_number)
                totals[key][0] += row.actual_seconds
                totals[key][1] += row.planned_seconds
                totals[key][2] += row.processed_count
    finally:
        if connection is None:
            own_connection.close()

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


def aggregate_by_machine_type(rows: list[UtilizationRow]) -> list[MachineTypeUtilizationRow]:
    """号機別のUtilizationRowを加工機タイプ単位(5号機分)に合算する(BR-8)。"""
    totals: dict[str, list[int]] = {m: [0, 0, 0] for m in MACHINE_TYPES}
    for row in rows:
        totals[row.machine_name][0] += row.actual_seconds
        totals[row.machine_name][1] += row.planned_seconds
        totals[row.machine_name][2] += row.processed_count

    results = []
    for machine_name, (actual_seconds, planned_seconds, processed_count) in totals.items():
        expected_seconds = processed_count * STANDARD_MINUTES[machine_name] * 60
        results.append(
            MachineTypeUtilizationRow(
                machine_name=machine_name,
                actual_seconds=actual_seconds,
                planned_seconds=planned_seconds,
                utilization_rate=_safe_rate(actual_seconds, planned_seconds),
                processed_count=processed_count,
                expected_utilization_rate=_safe_rate(expected_seconds, planned_seconds),
            )
        )
    return results


def aggregate_weekly_by_machine_type(rows: list[WeeklyUtilizationRow]) -> list[MachineTypeWeeklyUtilizationRow]:
    """週別のWeeklyUtilizationRowを加工機タイプ単位(5号機分)に合算する(BR-8)。"""
    totals: dict[str, list[int]] = {m: [0, 0, 0] for m in MACHINE_TYPES}
    for row in rows:
        totals[row.machine_name][0] += row.actual_seconds
        totals[row.machine_name][1] += row.planned_seconds
        totals[row.machine_name][2] += row.processed_count

    results = []
    for machine_name, (actual_seconds, planned_seconds, processed_count) in totals.items():
        expected_seconds = processed_count * STANDARD_MINUTES[machine_name] * 60
        results.append(
            MachineTypeWeeklyUtilizationRow(
                machine_name=machine_name,
                actual_seconds=actual_seconds,
                planned_seconds=planned_seconds,
                processed_count=processed_count,
                actual_utilization_rate=_safe_rate(actual_seconds, planned_seconds),
                expected_utilization_rate=_safe_rate(expected_seconds, planned_seconds),
            )
        )
    return results


def _fetch_aggregates_for_range(range_start: date, range_end: date, connection=None):
    own_connection = connection or get_connection()
    try:
        start_dt = datetime.combine(range_start, datetime.min.time())
        end_dt = datetime.combine(range_end, datetime.min.time())
        return fetch_range_aggregates(own_connection, start_dt, end_dt)
    finally:
        if connection is None:
            own_connection.close()


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
