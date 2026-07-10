# 追加機能サマリー - ポートフォリオ公開用デモダッシュボード

要件定義時点で「将来課題」としていた、Streamlit Community Cloud等への外部公開について、ユーザーからの要望（副業アピール用のポートフォリオとして公開したい）に応じて実装した。実際のSSMS(SQL Server Express)はローカルPC内にしかないため、クラウドから到達できない。この制約を回避するため、**本番用パイプラインとは完全に独立した「デモ専用」の仕組み**を新規に追加した。

## 設計方針
- 本番コード（`src/dashboard/`, `src/utilization/`, `src/db_loader/`, `src/csv_generator/`）には手を加えず、新規パッケージ`src/demo/`として実装（本番への影響ゼロ）
- データストアはSQLite（1ファイルで完結、サーバー不要、Streamlit Community Cloudでもそのまま動く）
- データ生成には既存の`CsvGenerator`のロジックをそのまま再利用（疑似データの品質・仕様は本番と同一）
- 集計ロジック（号機→加工機タイプへの合算等）も`src.utilization.calculator`のものをそのまま再利用し、クエリ層のみSQLite用に独自実装（T-SQLとSQLiteで日時パラメータの扱いが異なるため）
- チャート描画（`src.dashboard.charts`）・配色（`src.dashboard.config`）も本番と共通利用

## 生成したファイル
- `src/demo/generate_demo_data.py` — `CsvGenerator`を使い、直近90日分の疑似データをSQLiteファイル(`demo_data.db`)に生成
- `src/demo/calculator.py` — SQLite版の稼働率算出（`aggregate_by_machine_type`等は本番のものを再利用）
- `src/demo/data_service.py` — デモ用のトレンド・比較表データ整形（`src.dashboard.data_service`と同じ構造）
- `src/demo/app.py` — デモ専用のStreamlitエントリーポイント（「デモデータで動作しています」の注記付き）
- `src/demo/demo_data.db` — 事前生成した90日分のデモデータ（約2.8MB、リポジトリに同梱）

## 副次的な修正: pyodbcの遅延import
`src/db_loader/connection.py` と `src/utilization/connection.py` の `import pyodbc` をモジュール先頭から関数内（`get_connection()`呼び出し時）に変更した。デモは`db_loader`/`utilization`パッケージの一部ロジックを再利用するが、実DB接続は行わない。Streamlit Community Cloud(Linux)環境ではpyodbcの実行に必要なunixODBCが無い可能性があり、モジュール読み込み時にpyodbcをimportしていると、実際には使わないにもかかわらずimportエラーでアプリ全体が起動できなくなるおそれがあったため、予防的に修正した。本番の動作（Windows上でのSSMS接続）に変更はない。

## テスト
`tests/demo/`に8件のテストを追加（SQLite生成のスキーマ・日曜スキップ検証、稼働率算出の妥当性検証、集計ロジックの本番再利用の検証）。プロジェクト全体で計73テストが全てPASS。

## 動作確認
- `streamlit.testing.v1.AppTest` でヘッドレス実行し、例外なく動作することを確認
- 実際に90日分のデモデータで比較表を確認したところ、加工機C(ボトルネック)が最も高い稼働率(60%台)、他は加工時間に応じて相対的に低い値となり、設計意図通りの分布であることを確認

## デプロイ方法（Streamlit Community Cloud）
1. `share.streamlit.io` にログイン
2. 「New app」→ リポジトリ`Naoya-ya-man/Equipment_Operating_Rate`、ブランチ`main`、メインファイルパスに `src/demo/app.py` を指定
3. デプロイすると、リポジトリに同梱済みの`src/demo/demo_data.db`を使って即座に表示される（データが無ければ初回起動時に自動生成するフォールバックも実装済み）
4. 発行されたURLをポートフォリオ等で共有する

## 注意点
- デモデータは`src/demo/generate_demo_data.py`を再実行すると再生成される（都度ランダムに変わる、日付は実行時点までの直近90日分になる）。定期的に最新の日付に更新したい場合は再生成してコミットし直す
- 本番用の自動化（GitHub Actions、実SSMS）とは完全に独立しており、互いに影響しない

## 【実デプロイで発見・修正】表示基準日のずれ（2026-07-10）
Streamlit Community Cloudへの実デプロイ後、日別グラフの末尾（当日分）が0になる事象が発生した。原因は、`app.py`がグラフの基準日として実際のカレンダー上の「今日」(`date.today()`)を使っていたため。デモデータは静的な事前生成データであり、生成日以降の日付にはデータが存在しないため、閲覧するタイミングによっては末尾が空白/0になってしまう。

`src/demo/calculator.py`に`get_latest_data_date()`（デモDB内の`MAX(Processing_Start_Time)`を返す）を追加し、`app.py`側の基準日をこれに置き換えることで、閲覧タイミングに関わらず常にデータが揃った状態で表示されるように修正した。テスト1件追加、pytest 74件全てPASS。

## 自動更新の追加（2026-07-10）
ユーザーから「デモをリアルタイムに更新したい」との要望。デモデータ生成(`src/demo/generate_demo_data.py`)は実SSMSに一切依存しない自己完結型のPython処理（依存パッケージも標準ライブラリのみ。`pyodbc`遅延import化の効果で、`db_loader`パッケージのimport自体もpyodbc未インストール環境で動作することをクリーンな仮想環境で検証済み）であるため、本番と異なり**GitHubのホスト型ランナー**（PCの電源状態に依存しない）で定期実行できる。

`.github/workflows/refresh-demo-data.yml` を追加: 毎日UTC 18:00(JST 3:00)に`generate_demo_data`を再実行し、`demo_data.db`が変化していればコミット・プッシュする。プッシュされるとStreamlit Community Cloud側が自動的に再デプロイし、常に最新（直近90日分）のデモデータが表示され続ける。`workflow_dispatch`も併設し手動実行も可能。
