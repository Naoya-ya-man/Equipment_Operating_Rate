"""ダッシュボード表示用データの整形(UOW-4: DashboardApp)。"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Literal, Optional

import pandas as pd

from src.utilization.calculator import (
    aggregate_by_machine_type,
    aggregate_weekly_by_machine_type,
    get_daily_utilization,
    get_monthly_utilization,
    get_weekly_utilization,
)

Granularity = Literal["unit", "machine_type"]


def build_daily_trend(end_date: date, num_days: int, granularity: Granularity = "unit") -> pd.DataFrame:
    """直近num_days日分(end_date含む)の日別稼働率トレンドを構築する(BR-2)。"""
    records = []
    for offset in range(num_days - 1, -1, -1):
        target_date = end_date - timedelta(days=offset)
        rows = get_daily_utilization(target_date)
        if granularity == "machine_type":
            rows = aggregate_by_machine_type(rows)
        for row in rows:
            records.append(
                {
                    "target_date": target_date,
                    "series": _series_label(row.machine_name, getattr(row, "machine_number", None)),
                    "machine_name": row.machine_name,
                    "utilization_rate": row.utilization_rate,
                }
            )
    return pd.DataFrame(records)


def build_weekly_trend(end_date: date, num_weeks: int, granularity: Granularity = "unit") -> pd.DataFrame:
    """直近num_weeks週分(end_dateが属する週を含む)の週別稼働率トレンドを構築する(BR-3)。"""
    latest_monday = _monday_of(end_date)
    records = []
    for offset in range(num_weeks - 1, -1, -1):
        week_start = latest_monday - timedelta(weeks=offset)
        rows = get_weekly_utilization(week_start)
        if granularity == "machine_type":
            rows = aggregate_weekly_by_machine_type(rows)
        for row in rows:
            records.append(
                {
                    "week_start": week_start,
                    "series": _series_label(row.machine_name, getattr(row, "machine_number", None)),
                    "machine_name": row.machine_name,
                    "actual_rate": row.actual_utilization_rate,
                    "expected_rate": row.expected_utilization_rate,
                }
            )
    return pd.DataFrame(records)


def build_monthly_trend(end_date: date, num_months: int, granularity: Granularity = "unit") -> pd.DataFrame:
    """直近num_months ヶ月分(end_dateが属する月を含む)の月別稼働率トレンドを構築する(BR-4)。"""
    records = []
    for offset in range(num_months - 1, -1, -1):
        year, month = _shift_month(end_date.year, end_date.month, -offset)
        rows = get_monthly_utilization(year, month)
        if granularity == "machine_type":
            rows = aggregate_by_machine_type(rows)
        for row in rows:
            records.append(
                {
                    "year_month": f"{year:04d}-{month:02d}",
                    "series": _series_label(row.machine_name, getattr(row, "machine_number", None)),
                    "machine_name": row.machine_name,
                    "utilization_rate": row.utilization_rate,
                }
            )
    return pd.DataFrame(records)


def build_daily_comparison(target_date: date, granularity: Granularity = "unit") -> pd.DataFrame:
    """対象日の実績 vs 想定(理論値)の比較表を構築する。"""
    rows = get_daily_utilization(target_date)
    if granularity == "machine_type":
        rows = aggregate_by_machine_type(rows)
    return _rows_to_comparison_dataframe(rows)


def build_weekly_comparison(week_start: date, granularity: Granularity = "unit") -> pd.DataFrame:
    """対象週(月曜始まり)の実績 vs 想定(理論値)の比較表を構築する。"""
    rows = get_weekly_utilization(week_start)
    if granularity == "machine_type":
        rows = aggregate_weekly_by_machine_type(rows)
    return _rows_to_comparison_dataframe(rows)


def build_monthly_comparison(year: int, month: int, granularity: Granularity = "unit") -> pd.DataFrame:
    """対象月の実績 vs 想定(理論値)の比較表を構築する。"""
    rows = get_monthly_utilization(year, month)
    if granularity == "machine_type":
        rows = aggregate_by_machine_type(rows)
    return _rows_to_comparison_dataframe(rows)


def _rows_to_comparison_dataframe(rows) -> pd.DataFrame:
    """UtilizationRow/WeeklyUtilizationRow(またはそれらの加工機タイプ集計版)を、
    実績・想定(理論値)・差分を持つ比較用DataFrameに変換する。
    """
    records = []
    for row in rows:
        actual_rate = getattr(row, "actual_utilization_rate", None)
        if actual_rate is None:
            actual_rate = row.utilization_rate
        records.append(
            {
                "series": _series_label(row.machine_name, getattr(row, "machine_number", None)),
                "machine_name": row.machine_name,
                "processed_count": row.processed_count,
                "actual_rate": actual_rate,
                "expected_rate": row.expected_utilization_rate,
                "diff": round(actual_rate - row.expected_utilization_rate, 2),
            }
        )
    return pd.DataFrame(records)


def _series_label(machine_name: str, machine_number: Optional[int]) -> str:
    if machine_number is None:
        return machine_name
    return f"{machine_name}-{machine_number}"


def _monday_of(reference_date: date) -> date:
    return reference_date - timedelta(days=reference_date.weekday())


def _shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    index = (year * 12 + (month - 1)) + delta
    return index // 12, index % 12 + 1
