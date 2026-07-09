from src.scheduling import run_reporting_refresh
from src.utilization.models import UtilizationRow


def test_main_returns_zero_when_utilization_query_succeeds(monkeypatch):
    fake_rows = [
        UtilizationRow(
            machine_name="A",
            machine_number=1,
            actual_seconds=100,
            planned_seconds=86400,
            utilization_rate=0.1,
            processed_count=1,
            expected_utilization_rate=1.39,
        )
    ]
    monkeypatch.setattr(run_reporting_refresh, "get_daily_utilization", lambda target_date: fake_rows)

    assert run_reporting_refresh.main() == 0


def test_main_returns_one_when_utilization_query_raises(monkeypatch, capsys):
    def _raise(target_date):
        raise ConnectionError("DB unreachable")

    monkeypatch.setattr(run_reporting_refresh, "get_daily_utilization", _raise)

    exit_code = run_reporting_refresh.main()

    assert exit_code == 1
    assert "失敗" in capsys.readouterr().out
