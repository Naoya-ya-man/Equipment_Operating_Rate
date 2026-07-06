"""定期実行スクリプト(2): 稼働率算出の疎通確認(UOW-5: SchedulingOrchestration、補助経路)。

ダッシュボードはオンデマンドでUtilizationCalculatorを呼び出すため、本スクリプトは
定期実行のたびにSSMSへの参照が正常に行えることを確認する軽量な整合性チェックとして機能する。
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

_WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from src.utilization import get_daily_utilization  # noqa: E402


def main() -> int:
    today = date.today()
    try:
        rows = get_daily_utilization(today)
    except Exception as exc:  # noqa: BLE001 - 疎通確認の失敗をそのままジョブ失敗として通知する
        print(f"稼働率算出の疎通確認に失敗しました: {exc}")
        return 1

    print(f"稼働率算出の疎通確認: {today} の{len(rows)}件（号機別）を正常に取得しました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
