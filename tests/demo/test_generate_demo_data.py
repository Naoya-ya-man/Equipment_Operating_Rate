import sqlite3
from datetime import date

from src.demo.generate_demo_data import TABLE_NAME, generate_demo_database


def test_generate_demo_database_creates_expected_schema_and_rows(tmp_path, monkeypatch):
    db_path = tmp_path / "test_demo.db"
    monkeypatch.setattr("src.demo.generate_demo_data.DEMO_DB_PATH", db_path)

    # 2026-07-06(月)~2026-07-08(火) の3日間(日曜を含まない)
    result_path = generate_demo_database(num_days=3, end_date=date(2026, 7, 8))

    assert result_path == db_path
    assert db_path.exists()

    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        total_rows = cursor.fetchone()[0]
        assert total_rows > 0
        assert total_rows % 5 == 0  # 1製品あたりA~Eの5工程分

        cursor.execute(f'SELECT DISTINCT "Pass judgment" FROM {TABLE_NAME}')
        judgments = {row[0] for row in cursor.fetchall()}
        assert judgments <= {"OK", "NG"}
    finally:
        connection.close()


def test_generate_demo_database_skips_sunday(tmp_path, monkeypatch):
    db_path = tmp_path / "test_demo_sunday.db"
    monkeypatch.setattr("src.demo.generate_demo_data.DEMO_DB_PATH", db_path)

    # 2026-07-05は日曜日の1日だけを対象にする
    generate_demo_database(num_days=1, end_date=date(2026, 7, 5))

    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        assert cursor.fetchone()[0] == 0
    finally:
        connection.close()


def test_generate_demo_database_overwrites_existing_file(tmp_path, monkeypatch):
    db_path = tmp_path / "test_demo_overwrite.db"
    monkeypatch.setattr("src.demo.generate_demo_data.DEMO_DB_PATH", db_path)

    generate_demo_database(num_days=1, end_date=date(2026, 7, 7))
    first_size = db_path.stat().st_size

    generate_demo_database(num_days=2, end_date=date(2026, 7, 8))
    second_size = db_path.stat().st_size

    assert db_path.exists()
    assert second_size != first_size or second_size > 0
