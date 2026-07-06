# デプロイメントアーキテクチャ（UOW-5: SchedulingOrchestration）

## 構成図（ASCII）

```
+--------------------------------------------------------------+
|                     GitHub Actions (Cloud)                   |
|  - schedule: cron "0 3,15 * * *" (UTC) = JST 0:00 / 12:00     |
|  - workflow_dispatch (手動実行)                                |
+--------------------------------------------------------------+
                          | ジョブディスパッチ
                          v
+--------------------------------------------------------------+
|         Self-hosted Runner (ユーザーのローカルPC, Windows)      |
|                                                                |
|  1. actions/checkout                                          |
|  2. venv セットアップ + pip install -r requirements.txt        |
|  3. run_ingestion.py     -> CsvGenerator -> DbLoader           |
|  4. run_reporting_refresh.py -> UtilizationCalculator(疎通確認)|
|                                                                |
+--------------------------------------------------------------+
                          |
                          v (Windows統合認証)
+--------------------------------------------------------------+
|         SQL Server Express (.\SQLEXPRESS, ローカル)            |
|         Database: Equipment_Utilization_Rate                  |
+--------------------------------------------------------------+
```

## 依存関係
- `SchedulingOrchestration` は `CsvGenerator`, `DbLoader`, `UtilizationCalculator` の各エントリーポイント関数に依存する（新規インフラは持たず、既存コンポーネントを呼び出すのみ）
- DBインフラは新規構築せず、既存のローカルSQL Server Expressをそのまま使用する

## ロールバック戦略
- ワークフロー実行はSSMSへの書き込み（`DbLoader`のMERGE）を伴うが、UOW-2のBR-6（ファイル単位のトランザクション）により、失敗時は自動的にロールバックされる
- ワークフロー自体に問題があれば、`.github/workflows/scheduled-pipeline.yml` を修正し再実行（`workflow_dispatch`）すればよく、インフラの巻き戻しは不要
