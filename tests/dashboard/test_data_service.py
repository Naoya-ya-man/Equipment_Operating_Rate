from datetime import date

from src.dashboard import data_service
from src.utilization.models import UtilizationRow, WeeklyUtilizationRow


def _daily_rows(actual_seconds: int) -> list[UtilizationRow]:
    return [
        UtilizationRow(
            machine_name="A",
            machine_number=1,
            actual_seconds=actual_seconds,
            planned_seconds=86400,
            utilization_rate=1.0,
            processed_count=1,
            expected_utilization_rate=1.39,
        )
    ]


def test_build_daily_trend_covers_consecutive_days_ending_at_end_date(monkeypatch):
    calls = []

    def _fake_get_daily_utilization(target_date):
        calls.append(target_date)
        return _daily_rows(100)

    monkeypatch.setattr(data_service, "get_daily_utilization", _fake_get_daily_utilization)

    end_date = date(2026, 7, 10)
    df = data_service.build_daily_trend(end_date, num_days=3)

    assert calls == [date(2026, 7, 8), date(2026, 7, 9), date(2026, 7, 10)]
    assert list(df["target_date"]) == calls
    assert set(df["series"]) == {"A-1"}


def test_build_daily_trend_uses_machine_type_granularity(monkeypatch):
    from src.utilization.models import MachineTypeUtilizationRow

    monkeypatch.setattr(data_service, "get_daily_utilization", lambda target_date: _daily_rows(100))
    monkeypatch.setattr(
        data_service,
        "aggregate_by_machine_type",
        lambda rows: [
            MachineTypeUtilizationRow(
                machine_name="A",
                actual_seconds=100,
                planned_seconds=86400,
                utilization_rate=1.0,
                processed_count=1,
                expected_utilization_rate=1.39,
            )
        ],
    )

    df = data_service.build_daily_trend(date(2026, 7, 10), num_days=1, granularity="machine_type")

    assert list(df["series"]) == ["A"]  # 号機番号を含まない系列名


def test_build_weekly_trend_covers_consecutive_mondays(monkeypatch):
    calls = []

    def _fake_get_weekly_utilization(week_start):
        calls.append(week_start)
        return [
            WeeklyUtilizationRow(
                machine_name="A",
                machine_number=1,
                actual_seconds=1000,
                planned_seconds=486000,
                processed_count=2,
                actual_utilization_rate=0.2,
                expected_utilization_rate=0.5,
            )
        ]

    monkeypatch.setattr(data_service, "get_weekly_utilization", _fake_get_weekly_utilization)

    # 2026-07-10は金曜日 -> その週の月曜は2026-07-06
    df = data_service.build_weekly_trend(date(2026, 7, 10), num_weeks=2)

    assert calls == [date(2026, 6, 29), date(2026, 7, 6)]
    assert list(df["week_start"]) == calls


def test_build_monthly_trend_handles_year_rollover(monkeypatch):
    calls = []

    def _fake_get_monthly_utilization(year, month):
        calls.append((year, month))
        return _daily_rows(100)

    monkeypatch.setattr(data_service, "get_monthly_utilization", _fake_get_monthly_utilization)

    df = data_service.build_monthly_trend(date(2026, 2, 15), num_months=3)

    assert calls == [(2025, 12), (2026, 1), (2026, 2)]
    assert list(df["year_month"]) == ["2025-12", "2026-01", "2026-02"]


def test_build_daily_comparison_includes_actual_expected_and_diff(monkeypatch):
    monkeypatch.setattr(data_service, "get_daily_utilization", lambda target_date: _daily_rows(100))

    df = data_service.build_daily_comparison(date(2026, 7, 10))

    assert list(df["series"]) == ["A-1"]
    row = df.iloc[0]
    assert row["processed_count"] == 1
    assert row["actual_rate"] == 1.0
    assert row["expected_rate"] == 1.39
    assert row["diff"] == round(1.0 - 1.39, 2)


def test_build_weekly_comparison_uses_actual_utilization_rate_field(monkeypatch):
    monkeypatch.setattr(
        data_service,
        "get_weekly_utilization",
        lambda week_start: [
            WeeklyUtilizationRow(
                machine_name="A",
                machine_number=1,
                actual_seconds=1000,
                planned_seconds=486000,
                processed_count=2,
                actual_utilization_rate=20.0,
                expected_utilization_rate=50.0,
            )
        ],
    )

    df = data_service.build_weekly_comparison(date(2026, 7, 6))

    row = df.iloc[0]
    assert row["actual_rate"] == 20.0
    assert row["expected_rate"] == 50.0
    assert row["diff"] == -30.0


def test_build_monthly_comparison_by_machine_type(monkeypatch):
    from src.utilization.models import MachineTypeUtilizationRow

    monkeypatch.setattr(data_service, "get_monthly_utilization", lambda year, month: _daily_rows(100))
    monkeypatch.setattr(
        data_service,
        "aggregate_by_machine_type",
        lambda rows: [
            MachineTypeUtilizationRow(
                machine_name="A",
                actual_seconds=500,
                planned_seconds=432000,
                utilization_rate=0.12,
                processed_count=5,
                expected_utilization_rate=1.39,
            )
        ],
    )

    df = data_service.build_monthly_comparison(2026, 7, granularity="machine_type")

    assert list(df["series"]) == ["A"]  # 号機番号を含まない系列名
    assert df.iloc[0]["processed_count"] == 5
