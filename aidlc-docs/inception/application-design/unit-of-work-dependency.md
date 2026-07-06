# ユニット間依存関係（Unit of Work Dependency）

## 依存関係マトリクス

| ユニット | 依存先ユニット | 依存の理由 |
|---|---|---|
| UOW-1: CsvGenerator | なし | 純粋なデータ生成、外部依存なし |
| UOW-2: DbLoader | UOW-1 | CSVフォーマット（カラム定義）に依存 |
| UOW-3: UtilizationCalculator | UOW-2 | SSMSのテーブルスキーマ・投入データに依存 |
| UOW-4: DashboardApp | UOW-3 | 稼働率データの戻り値形式に依存 |
| UOW-5: SchedulingOrchestration | UOW-1, UOW-2, UOW-3 | 各ユニットのCLIエントリーポイントを呼び出して統合するため |

## 統合ポイント・契約
- **UOW-1 → UOW-2**: `A1_ProcessingMachine_Utilization_Rate.csv` のカラム定義（7カラム、型、順序）が契約
- **UOW-2 → UOW-3**: SSMSテーブル `[dbo].[A1_ProcessingMachine_Utilization_Rate]` のスキーマ・インデックスが契約
- **UOW-3 → UOW-4**: `get_daily_utilization` / `get_weekly_utilization` / `get_monthly_utilization` の戻り値（号機別稼働率テーブル）が契約
- **UOW-5 → UOW-1/2/3**: 各ユニットのCLIエントリーポイント（`run_ingestion_pipeline`, `run_reporting_refresh` から呼び出される関数）が契約

## ビルド・開発順序の制約

**推奨する構築順序**: UOW-1 → UOW-2 → UOW-3 → UOW-4 → UOW-5

- 基本はパイプラインの上流から下流に向かって開発する（データがないと下流の動作確認ができないため）
- UOW-3（稼働率算出）とUOW-4（ダッシュボード）はモックデータを使えば、UOW-2の完了を待たずに並行して着手することも可能
- UOW-5（定期実行基盤）は他の全ユニットのCLIエントリーポイントが揃った後に統合するため、最後に着手する
