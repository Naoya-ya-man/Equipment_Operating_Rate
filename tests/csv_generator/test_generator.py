import csv
from datetime import datetime

from src.csv_generator.config import CSV_COLUMNS, OUTPUT_DIR_NAME, OUTPUT_FILE_NAME
from src.csv_generator.generator import generate_daily_csv


def test_generate_daily_csv_skips_sunday(tmp_path):
    sunday_morning = datetime(2026, 7, 5, 3, 0)  # 日曜日
    result = generate_daily_csv(reference_time=sunday_morning, workspace_root=tmp_path)

    assert result is None
    assert not (tmp_path / OUTPUT_DIR_NAME / OUTPUT_FILE_NAME).exists()


def test_generate_daily_csv_creates_csv_with_valid_rows(tmp_path):
    tuesday_morning = datetime(2026, 7, 7, 1, 0)  # 火曜日
    result = generate_daily_csv(reference_time=tuesday_morning, workspace_root=tmp_path)

    assert result is not None
    assert result == tmp_path / OUTPUT_DIR_NAME / OUTPUT_FILE_NAME
    assert result.exists()

    with result.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    assert header == CSV_COLUMNS
    # 各チェーンは5行(A〜E)のため、行数は5の倍数であること
    assert len(rows) % 5 == 0

    for row in rows:
        pass_judgment = row[-1]
        assert pass_judgment in ("OK", "NG")
