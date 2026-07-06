# コード生成サマリー - UOW-3: UtilizationCalculator

## 生成したファイル（アプリケーションコード、ワークスペースルート配下）

- `src/utilization/__init__.py` — パッケージエントリーポイント
- `src/utilization/config.py` — DB接続先・加工機タイプ・標準加工時間・計画時間定数
- `src/utilization/models.py` — `UtilizationRow`, `WeeklyUtilizationRow`, `MachineTypeUtilizationRow`, `MachineTypeWeeklyUtilizationRow`
- `src/utilization/planned_time.py` — 計画時間(分母)の算出（BR-1）
- `src/utilization/connection.py` — Windows統合認証・ODBCドライバのフォールバック接続
- `src/utilization/queries.py` — 号機別の実加工時間・件数を集計するSQLクエリ（UOW-2のインデックスを活用）
- `src/utilization/calculator.py` — エントリーポイント: `get_daily_utilization()`, `get_weekly_utilization()`, `get_monthly_utilization()`, `aggregate_by_machine_type()`, `aggregate_weekly_by_machine_type()`

## 生成したテスト（DB接続はモック）

- `tests/utilization/test_planned_time.py` — 計画時間算出（日曜0、月曜補正、通常日）の検証
- `tests/utilization/test_queries.py` — クエリ結果のdict変換、NULL値の扱いの検証
- `tests/utilization/test_calculator.py` — 日別/週別/月別の算出、ゼロ除算回避、加工機タイプ単位の集計（BR-8）の検証

**テスト結果**: 12件すべてPASS。プロジェクト全体では計40件すべてPASS（UOW-1〜UOW-3、回帰なし）

## ユーザー追加要望への対応（BR-8）
「号機ごと及び加工機ごとの想定稼働率がわかれば好ましい」との要望を受け、号機単位(25件)の結果に加えて、加工機タイプ単位(5号機を合算した5件)の集計を `aggregate_by_machine_type()` / `aggregate_weekly_by_machine_type()` として実装した。追加のSQLクエリは発生させず、既存の号機別結果をPython側で合算する設計とした。

## 実運用に向けた注意点
- UOW-2と同様、実際のSSMS環境での接続確認はこの開発環境では未検証
- `get_monthly_utilization()` は日別クエリを月内の日数分繰り返すため、月の日数分のDBラウンドトリップが発生する（1ヶ月あたり最大31回）。現状のデータ量では許容範囲だが、将来的にデータ量が増えた場合は月単位の一括集計クエリへの最適化を検討の余地がある
