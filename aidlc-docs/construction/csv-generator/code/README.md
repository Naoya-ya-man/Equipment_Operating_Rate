# コード生成サマリー - UOW-1: CsvGenerator

## 生成したファイル（アプリケーションコード、ワークスペースルート配下）

- `src/csv_generator/__init__.py` — パッケージエントリーポイント（`generate_daily_csv` を公開）
- `src/csv_generator/config.py` — 標準加工時間・休憩時間帯・NG率(3%)・設備停止率(1%)等のパラメータ
- `src/csv_generator/models.py` — `ExecutionWindow`, `ProcessingRecord`, `ProductChain` エンティティ
- `src/csv_generator/calendar_utils.py` — 実行窓(12時間)の決定、稼働可能秒数の算出（BR-1, BR-2）
- `src/csv_generator/capacity.py` — ボトルネック工程(加工機C)基準の理論生産数上限算出（BR-3）
- `src/csv_generator/chain_builder.py` — A→B→C→D→E製品チェーン生成、実行窓をまたがない制約、号機均等配分（BR-5〜BR-10）
- `src/csv_generator/generator.py` — エントリーポイント `generate_daily_csv()`、CSV出力（`データ転送前/A1_ProcessingMachine_Utilization_Rate.csv`）

## 生成したテスト

- `tests/csv_generator/test_calendar_utils.py` — 日曜全休・月曜補正・休憩時間判定の検証
- `tests/csv_generator/test_capacity.py` — 理論生産数上限の計算検証
- `tests/csv_generator/test_chain_builder.py` — 製品チェーンの5工程整合性・時系列整合性・号機均等配分の検証
- `tests/csv_generator/test_generator.py` — CSV出力の検証（日曜スキップ、ヘッダー、行数が5の倍数であること等）

**テスト結果**: 14件すべてPASS（`pytest tests/csv_generator`）

## その他の生成物

- `requirements.txt`（ワークスペースルート） — `pytest` を追加
- `.gitignore`（ワークスペースルート） — `.venv/`, `__pycache__/`, `.pytest_cache/` を除外

## テスト中に発見・修正したバグ

1. **休憩時間の二重カウント**: 月曜の非稼働時間(0:00-9:00)と、その時間帯に含まれる休憩(2:00-2:45, 5:00-5:15)を別々に減算していたため、稼働可能秒数が過小評価されていた。区間をマージしてから合計する方式に修正。
2. **生成開始カーソルの不整合**: 月曜日でも実行窓の開始(0:00)からチェーン生成を始めており、非稼働時間帯(0:00-9:00)にデータが生成されうる状態だった。`ExecutionWindow.earliest_start` を追加し、非稼働時間を除いた最初の稼働開始時刻からチェーン生成するよう修正。

## 手動実行での動作確認
2026-07-04〜2026-08-02の30日分(60実行窓)をシミュレーションし、例外なく動作すること、日曜は生成スキップ、月曜朝の窓は生成数が少なくなる（稼働可能時間が短いため）ことを確認済み。
