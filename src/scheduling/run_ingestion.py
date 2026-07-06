"""定期実行スクリプト(1): CSV生成 + SSMS取り込み(UOW-5: SchedulingOrchestration)。

GitHub Actions(Self-hosted Runner)から `python src/scheduling/run_ingestion.py` として実行される。
"""
from __future__ import annotations

import sys
from pathlib import Path

_WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from src.csv_generator import generate_daily_csv  # noqa: E402
from src.db_loader import load_pending_csv_files  # noqa: E402


def main() -> int:
    csv_path = generate_daily_csv()
    if csv_path is None:
        print("CSV生成: 実行窓が日曜日のためスキップしました。")
    else:
        print(f"CSV生成: {csv_path}")

    results = load_pending_csv_files()
    if not results:
        print("DB取り込み: 対象CSVファイルはありませんでした。")

    failure_count = 0
    for result in results:
        status = "OK" if result.success else f"ERROR: {result.error_message}"
        print(f"DB取り込み: {result.file_path.name}: {status} ({result.row_count} rows)")
        if not result.success:
            failure_count += 1

    return 1 if failure_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
