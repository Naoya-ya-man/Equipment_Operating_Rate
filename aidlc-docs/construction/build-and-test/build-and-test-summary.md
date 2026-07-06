# ビルド・テストサマリー

## ビルドステータス
- **ツール**: venv + pip（`requirements.txt`: pytest, pyodbc, pandas, plotly, streamlit）
- **ステータス**: 成功
- **成果物**: `.venv/`（Gitには含めない）

## ユニットテスト
| ユニット | テスト件数 | 結果 |
|---|---|---|
| UOW-1: CsvGenerator | 14 | PASS |
| UOW-2: DbLoader | 14 | PASS |
| UOW-3: UtilizationCalculator | 12 | PASS |
| UOW-4: DashboardApp | 13 | PASS |
| UOW-5: SchedulingOrchestration | 5 | PASS |
| **合計** | **58** | **全件PASS** |

- カバレッジ計測ツールは未導入（プロジェクト規模を踏まえ、Liteの効率性重視の方針でスコープ外とした）
- 実行時間: 数秒程度（全テストがDB接続をモック化しているため高速）

## 統合テスト
| シナリオ | 結果 |
|---|---|
| CsvGenerator出力のDbLoaderによる読み込み・型変換 | PASS |
| CsvGenerator → UtilizationCalculator → DashboardAppの一気通貫データ連携 | PASS |
| **合計** | **2件 全件PASS** |

## 追加テスト
| 種別 | ステータス |
|---|---|
| パフォーマンステスト | N/A（明示的な性能NFRなし。UOW-3の月次クエリのDBラウンドトリップ回数のみ既知の最適化余地として記録済み） |
| コントラクトテスト | N/A（マイクロサービス構成ではないモノリスのため対象外） |
| セキュリティテスト | N/A（セキュリティ拡張は未オプトイン。Windows統合認証のためシークレット管理も不要） |
| E2Eテスト | 手動検証手順として`build-and-test-instructions.md`に記載（実SSMS接続・実Streamlit起動を伴うため自動化は将来検討） |

## 開発中に発見・修正した主なバグ（累計4件）
1. CsvGenerator: 月曜日の非稼働時間と休憩時間の二重カウント
2. CsvGenerator: 月曜日の生成開始カーソルが非稼働時間帯を考慮していなかった
3. DbLoader: `schema.sql`の説明コメントが区切り文字列を含んでいたことによる誤分割
4. DashboardApp: `streamlit run`実行時の相対importエラー、および非推奨API(`use_container_width`)の使用

## 総合ステータス
- **ビルド結果**: 成功
- **全テスト結果**: 成功（ユニット58件 + 統合2件 = 60件全件PASS）
- **Operationsフェーズへの準備**: 部分的に可（アプリケーションコードは完成・テスト済みだが、以下はユーザー側の実環境での作業が必要）
  - Self-hosted Runnerのセットアップ（GitHubリポジトリへの登録、サービス化、スリープ無効化）
  - SSMS上での`Equipment_Utilization_Rate`データベースの作成（未作成の場合）
  - 実際のGitHub Actions実行・実SSMS接続での動作確認（この開発環境では未検証）

## 次のステップ
Operationsフェーズは現バージョンではプレースホルダーのため、実運用に向けては上記の「ユーザー側の作業」を完了させたうえで、`build-and-test-instructions.md`の検証手順に沿って実環境での動作確認を行うことを推奨する。
