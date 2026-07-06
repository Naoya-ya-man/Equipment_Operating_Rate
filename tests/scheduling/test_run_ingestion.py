from pathlib import Path

from src.db_loader.models import LoadResult
from src.scheduling import run_ingestion


def test_main_returns_zero_when_sunday_skip_and_no_pending_files(monkeypatch, capsys):
    monkeypatch.setattr(run_ingestion, "generate_daily_csv", lambda: None)
    monkeypatch.setattr(run_ingestion, "load_pending_csv_files", lambda: [])

    exit_code = run_ingestion.main()

    assert exit_code == 0
    assert "スキップ" in capsys.readouterr().out


def test_main_returns_zero_when_all_files_succeed(monkeypatch):
    monkeypatch.setattr(run_ingestion, "generate_daily_csv", lambda: Path("dummy.csv"))
    monkeypatch.setattr(
        run_ingestion,
        "load_pending_csv_files",
        lambda: [LoadResult(file_path=Path("dummy.csv"), success=True, row_count=25)],
    )

    assert run_ingestion.main() == 0


def test_main_returns_one_when_any_file_fails(monkeypatch):
    monkeypatch.setattr(run_ingestion, "generate_daily_csv", lambda: Path("dummy.csv"))
    monkeypatch.setattr(
        run_ingestion,
        "load_pending_csv_files",
        lambda: [
            LoadResult(file_path=Path("ok.csv"), success=True, row_count=5),
            LoadResult(file_path=Path("bad.csv"), success=False, row_count=0, error_message="boom"),
        ],
    )

    assert run_ingestion.main() == 1
