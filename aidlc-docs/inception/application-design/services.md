# サービス定義（Services）

## DataPipelineService
**責務**: データ生成からDB取り込みまでの一連の処理をオーケストレーションする。
- 呼び出し順序: `CsvGenerator.generate_daily_csv()` → `DbLoader.load_csv_to_db()`
- GitHub Actions（Self-hosted Runner）から `SchedulingOrchestration.run_ingestion_pipeline()` 経由で12時間毎に起動される
- 手動実行（ローカルCLI）にも対応できるようにする（デバッグ・初回データ投入用）

## UtilizationReportingService
**責務**: SSMSのデータから稼働率を算出し、WEB画面に反映するオーケストレーション。
- 主経路: `DashboardApp` がユーザーのブラウザアクセス時に `UtilizationCalculator` を直接呼び出し、その場でSSMSを参照して最新の稼働率を算出・表示する（リアルタイム表示）
- 補助経路: GitHub Actionsの定期実行（`SchedulingOrchestration.run_reporting_refresh()`）は、将来的なキャッシュ/事前計算の最適化ポイントとして予約する（現時点ではDashboardAppのオンデマンド計算が主であり、このスクリプトは軽量な整合性チェック用途を想定）

## SchedulingOrchestration Service
**責務**: GitHub Actionsワークフロー定義を通じて、上記2サービスを12時間毎の順序で実行する。
- 実行順序: `DataPipelineService` → `UtilizationReportingService`（補助経路）
- 実行環境: ローカルPCに構築したSelf-hosted Runner
