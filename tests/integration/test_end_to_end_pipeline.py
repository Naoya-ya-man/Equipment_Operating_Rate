"""統合テスト: CsvGenerator -> DbLoader -> UtilizationCalculator -> DashboardApp のデータ連携を検証する。

実際のSSMS接続は行わず、CsvGeneratorが生成したCSVをそのまま集計元データとして使うことで、
ユニット間のデータ形式・カラム定義の整合性を確認する(実DB接続はいずれのユニットのテストでも未検証、
`aidlc-docs/construction/*/code/README.md` に既知の制約として記載済み)。
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from unittest.mock import MagicMock

from src.csv_generator.generator import generate_daily_csv
from src.dashboard import data_service
from src.dashboard.charts import build_daily_line_chart
from src.db_loader.csv_reader import read_csv_records
from src.utilization import calculator


def test_csv_generator_output_is_readable_by_db_loader(tmp_path):
    """UOW-1が生成するCSVのカラム構成・型が、UOW-2の読み込み・型変換とかみ合うことを確認する。"""
    csv_path = generate_daily_csv(reference_time=datetime(2026, 7, 7, 0, 0), workspace_root=tmp_path)
    assert csv_path is not None

    records = read_csv_records(csv_path)
    assert len(records) % 5 == 0  # 1製品あたりA~Eの5工程分
    assert all(isinstance(record.machine_number, str) for record in records)
    assert all(record.pass_judgment in ("OK", "NG") for record in records)


def test_full_pipeline_from_csv_to_dashboard_chart(monkeypatch, tmp_path):
    """CSV生成結果を疑似DBとして、UtilizationCalculator・DashboardAppまで一気通貫でデータが流れることを確認する。"""
    reference_time = datetime(2026, 7, 7, 0, 0)  # 火曜日(通常稼働日)
    csv_path = generate_daily_csv(reference_time=reference_time, workspace_root=tmp_path)
    db_records = read_csv_records(csv_path)
    assert db_records  # 通常稼働日のため必ず1件以上生成される

    # DbLoaderがMERGEするSSMSテーブルの代わりに、号機別の実加工時間・件数をメモリ上に集計する
    fake_db: dict[tuple[str, int], list[int]] = defaultdict(lambda: [0, 0])
    for record in db_records:
        key = (record.machine_name, int(record.machine_number))
        fake_db[key][0] += record.sum_datetime
        fake_db[key][1] += 1

    monkeypatch.setattr(calculator, "get_connection", lambda: MagicMock())
    monkeypatch.setattr(
        calculator,
        "fetch_range_aggregates",
        lambda conn, start, end: {key: tuple(value) for key, value in fake_db.items()},
    )

    daily_df = data_service.build_daily_trend(reference_time.date(), num_days=1)

    assert len(daily_df) == 25  # 全加工機タイプ(A~E) x 全号機(1~5)

    for (machine_name, machine_number), (actual_seconds, _) in fake_db.items():
        series_row = daily_df[(daily_df["machine_name"] == machine_name) & (daily_df["series"] == f"{machine_name}-{machine_number}")]
        assert series_row.iloc[0]["utilization_rate"] == round(actual_seconds / 86400 * 100, 2)

    figure = build_daily_line_chart(daily_df)
    assert len(figure.data) == 25
