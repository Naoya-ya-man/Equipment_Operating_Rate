from datetime import date

import pytest

from src.demo import calculator
from src.demo.generate_demo_data import generate_demo_database


@pytest.fixture
def demo_db(tmp_path, monkeypatch):
    db_path = tmp_path / "calc_test.db"
    monkeypatch.setattr("src.demo.generate_demo_data.DEMO_DB_PATH", db_path)
    monkeypatch.setattr(calculator, "DEMO_DB_PATH", db_path)
    # 2026-07-06(月)~2026-07-08(火)の3日間を生成
    generate_demo_database(num_days=3, end_date=date(2026, 7, 8))
    return db_path


def test_get_daily_utilization_returns_25_rows_with_plausible_rates(demo_db):
    rows = calculator.get_daily_utilization(date(2026, 7, 7))  # 火曜日(通常稼働日)

    assert len(rows) == 25
    # 通常稼働日であれば、少なくとも一部の号機にデータが投入されているはず
    assert any(r.actual_seconds > 0 for r in rows)
    assert all(0 <= r.utilization_rate <= 100 for r in rows)
    assert all(r.expected_utilization_rate >= 0 for r in rows)


def test_get_weekly_utilization_requires_monday(demo_db):
    with pytest.raises(ValueError):
        calculator.get_weekly_utilization(date(2026, 7, 7))


def test_get_weekly_utilization_returns_25_rows(demo_db):
    rows = calculator.get_weekly_utilization(date(2026, 7, 6))  # 月曜日
    assert len(rows) == 25
    assert all(r.processed_count >= 0 for r in rows)


def test_get_monthly_utilization_aggregates_generated_days(demo_db):
    rows = calculator.get_monthly_utilization(2026, 7)
    assert len(rows) == 25
    # 生成した7/6~7/8分の実績が月次集計に反映されているはず
    assert sum(r.actual_seconds for r in rows) > 0


def test_aggregate_by_machine_type_is_reexported_from_real_calculator():
    from src.utilization.calculator import aggregate_by_machine_type as real_aggregate

    assert calculator.aggregate_by_machine_type is real_aggregate
