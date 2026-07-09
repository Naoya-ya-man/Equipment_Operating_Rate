from datetime import date
from unittest.mock import MagicMock

import pytest

from src.utilization import calculator
from src.utilization.models import UtilizationRow, WeeklyUtilizationRow


@pytest.fixture(autouse=True)
def _mock_connection(monkeypatch):
    monkeypatch.setattr(calculator, "get_connection", lambda: MagicMock())


def test_get_daily_utilization_returns_25_rows_with_expected_defaults(monkeypatch):
    tuesday = date(2026, 7, 7)
    # A-1号機: 2件処理、実加工1200秒(標準20分=1200秒 -> 期待2*1200=2400秒)
    monkeypatch.setattr(calculator, "fetch_range_aggregates", lambda conn, start, end: {("A", 1): (1200, 2)})

    rows = calculator.get_daily_utilization(tuesday)

    assert len(rows) == 25
    target = next(r for r in rows if r.machine_name == "A" and r.machine_number == 1)
    assert target.actual_seconds == 1200
    assert target.planned_seconds == 86400
    assert target.utilization_rate == round(1200 / 86400 * 100, 2)
    assert target.processed_count == 2
    assert target.expected_utilization_rate == round(2 * 1200 / 86400 * 100, 2)

    other = next(r for r in rows if r.machine_name == "B" and r.machine_number == 2)
    assert other.actual_seconds == 0
    assert other.utilization_rate == 0.0
    assert other.processed_count == 0
    assert other.expected_utilization_rate == 0.0


def test_get_daily_utilization_sunday_avoids_division_by_zero(monkeypatch):
    sunday = date(2026, 7, 5)
    monkeypatch.setattr(calculator, "fetch_range_aggregates", lambda conn, start, end: {("A", 1): (100, 1)})

    rows = calculator.get_daily_utilization(sunday)

    target = next(r for r in rows if r.machine_name == "A" and r.machine_number == 1)
    assert target.planned_seconds == 0
    assert target.utilization_rate == 0.0  # ゼロ除算を回避(BR-2)


def test_get_weekly_utilization_requires_monday_start():
    tuesday = date(2026, 7, 7)
    with pytest.raises(ValueError):
        calculator.get_weekly_utilization(tuesday)


def test_get_weekly_utilization_computes_actual_and_expected_rates(monkeypatch):
    monday = date(2026, 7, 6)  # 週: 7/6(月)～7/12(日)
    # A-1号機: 週間で3600秒実加工、5件処理(標準20分=1200秒 -> 期待5*1200=6000秒)
    monkeypatch.setattr(calculator, "fetch_range_aggregates", lambda conn, start, end: {("A", 1): (3600, 5)})

    rows = calculator.get_weekly_utilization(monday)
    assert len(rows) == 25

    # 週間計画時間 = 月(54000) + 火~土(5*86400) + 日(0) = 486000秒
    expected_total_planned = (86400 - 9 * 3600) + 5 * 86400 + 0
    target = next(r for r in rows if r.machine_name == "A" and r.machine_number == 1)
    assert target.planned_seconds == expected_total_planned
    assert target.processed_count == 5
    assert target.actual_utilization_rate == round(3600 / expected_total_planned * 100, 2)
    assert target.expected_utilization_rate == round(6000 / expected_total_planned * 100, 2)


def test_get_monthly_utilization_sums_daily_rows(monkeypatch):
    fake_row = UtilizationRow(
        machine_name="A",
        machine_number=1,
        actual_seconds=100,
        planned_seconds=86400,
        utilization_rate=0.12,
        processed_count=1,
        expected_utilization_rate=1.39,
    )

    def _fake_get_daily_utilization(target_date, connection=None):
        return [fake_row]

    monkeypatch.setattr(calculator, "get_daily_utilization", _fake_get_daily_utilization)

    rows = calculator.get_monthly_utilization(2026, 2)  # 2026年2月 = 28日間

    assert len(rows) == 25
    target = next(r for r in rows if r.machine_name == "A" and r.machine_number == 1)
    assert target.actual_seconds == 100 * 28
    assert target.planned_seconds == 86400 * 28
    assert target.processed_count == 1 * 28
    expected_seconds = 28 * 20 * 60  # processed_count合算(28) x 標準加工時間(A=20分)
    assert target.expected_utilization_rate == round(expected_seconds / (86400 * 28) * 100, 2)


def test_aggregate_by_machine_type_sums_five_units():
    rows = [
        UtilizationRow(
            machine_name="A",
            machine_number=n,
            actual_seconds=100,
            planned_seconds=86400,
            utilization_rate=0.1,
            processed_count=1,
            expected_utilization_rate=1.39,
        )
        for n in range(1, 6)
    ] + [
        UtilizationRow(
            machine_name="B",
            machine_number=n,
            actual_seconds=200,
            planned_seconds=86400,
            utilization_rate=0.2,
            processed_count=2,
            expected_utilization_rate=4.17,
        )
        for n in range(1, 6)
    ]

    aggregated = calculator.aggregate_by_machine_type(rows)

    assert len(aggregated) == 5
    machine_a = next(r for r in aggregated if r.machine_name == "A")
    assert machine_a.actual_seconds == 500
    assert machine_a.planned_seconds == 86400 * 5
    assert machine_a.utilization_rate == round(500 / (86400 * 5) * 100, 2)
    assert machine_a.processed_count == 5
    expected_seconds = 5 * 20 * 60  # processed_count合算(5) x 標準加工時間(A=20分)
    assert machine_a.expected_utilization_rate == round(expected_seconds / (86400 * 5) * 100, 2)


def test_aggregate_weekly_by_machine_type_sums_five_units():
    rows = [
        WeeklyUtilizationRow(
            machine_name="A",
            machine_number=n,
            actual_seconds=1000,
            planned_seconds=486000,
            processed_count=2,
            actual_utilization_rate=0.2,
            expected_utilization_rate=0.5,
        )
        for n in range(1, 6)
    ]

    aggregated = calculator.aggregate_weekly_by_machine_type(rows)

    assert len(aggregated) == 5
    machine_a = next(r for r in aggregated if r.machine_name == "A")
    assert machine_a.actual_seconds == 5000
    assert machine_a.processed_count == 10
    assert machine_a.planned_seconds == 486000 * 5
    expected_seconds = 10 * 20 * 60  # processed_count合算 x 標準加工時間(A=20分)
    assert machine_a.expected_utilization_rate == round(expected_seconds / (486000 * 5) * 100, 2)
