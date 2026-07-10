# コード生成サマリー - UOW-5: SchedulingOrchestration

## 生成したファイル（アプリケーションコード、ワークスペースルート配下）

- `src/scheduling/run_ingestion.py` — スクリプト①: CSV生成(`CsvGenerator`) → SSMS取り込み(`DbLoader`)。失敗ファイルがあれば非ゼロ終了
- `src/scheduling/run_reporting_refresh.py` — スクリプト②: 稼働率算出(`UtilizationCalculator`)の疎通確認（補助経路）。例外時は非ゼロ終了
- `.github/workflows/scheduled-pipeline.yml` — GitHub Actionsワークフロー定義（Self-hosted Runner、12時間毎のcronスケジュール、`workflow_dispatch`併設）
- `データ転送前/.gitkeep`, `データ転送後/.gitkeep`, `エラー項目/.gitkeep` — Gitが空フォルダを追跡しないため追加

## 生成したテスト

- `tests/scheduling/test_run_ingestion.py` — 日曜スキップ時・全件成功時・一部失敗時の終了コード検証
- `tests/scheduling/test_run_reporting_refresh.py` — 成功時・DB接続エラー時の終了コード検証

**テスト結果**: 5件すべてPASS。プロジェクト全体（UOW-1〜5）で計58件すべてPASS

## 実際のスクリプト実行による動作確認
`.venv\Scripts\python.exe src\scheduling\run_ingestion.py` および `run_reporting_refresh.py` を、GitHub Actionsが実行するのと同じ「ワークスペースルートからのスクリプト直接実行」の形で実際に動かし、正常終了(exit code 0)することを確認した（UOW-4で発見した相対import問題を踏まえ、本ユニットでは最初から絶対import + `sys.path`ブートストラップを採用済み）。2026-07-05(日曜日)に実行したため、CSV生成は正しくスキップされ、稼働率算出の疎通確認は正常に完了した。

## インフラ設計での重要な発見（再掲）
GitHub Actionsの`schedule`はUTCで解釈されるため、JST 0:00/12:00に実行するには `cron: "0 3,15 * * *"` が必要（詳細は `aidlc-docs/construction/scheduling-orchestration/infrastructure-design/`）。

## 実運用に向けた注意点
- Self-hosted Runnerのセットアップ（GitHubリポジトリへの登録、サービス化）はユーザー側の作業として残っている
- 実際のSSMS接続・実際のGitHub Actions実行環境での動作確認はこの開発環境では未検証

## 【実環境での初回実行で発見・修正】`shell: pwsh` が使えない（2026-07-08）
ユーザーがSelf-hosted Runnerをセットアップし、実際にワークフローを実行したところ、以下のエラーで失敗した:
```
Error: pwsh: command not found
```
**原因**: `scheduled-pipeline.yml` の各ステップで `shell: pwsh`（PowerShell 7/Core）を指定していたが、ユーザーのPCにはPowerShell 7がインストールされておらず、標準搭載のWindows PowerShell（`powershell.exe`、5.1系）のみが存在していた。開発環境ではワークフローYAML自体の実行検証（実際にRunner上で動かす）ができなかったため、この不一致は検出できなかった。

**修正内容**: `scheduled-pipeline.yml` の3ステップ全ての `shell: pwsh` を `shell: powershell`（Windows PowerShell 5.1、全Windows環境に標準搭載）に変更。スクリプトの記述内容自体はPowerShell 5.1でもそのまま動作するため、他の変更は不要だった。

修正後、ユーザー環境での再実行による確認が次のステップ。
