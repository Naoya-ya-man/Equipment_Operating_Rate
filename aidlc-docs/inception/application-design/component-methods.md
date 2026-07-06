# コンポーネントメソッド定義（Component Methods）

> 詳細なビジネスルールはCONSTRUCTIONフェーズの各ユニットのFunctional Designで定義する。ここではメソッドシグネチャと目的のみを示す。

## CsvGenerator
| メソッド | 入力 | 出力 | 目的 |
|---|---|---|---|
| `generate_daily_csv(target_date)` | 対象日(date) | CSVファイルパス（日曜はNone） | その日の疑似データCSVを`データ転送前/`に生成 |
| `compute_daily_capacity(target_date, machine_type)` | 対象日, 加工機タイプ | 理論生産数上限(int) | 稼働可能秒数とボトルネックから理論上限を算出 |
| `build_product_chain(base_product_id, machine_assignments)` | 品番ベース, 号機割当 | CSV行のリスト(A~E, 5行) | 1製品のA→B→C→D→E工程分のレコードを時系列整合性を保って生成 |

## DbLoader
| メソッド | 入力 | 出力 | 目的 |
|---|---|---|---|
| `load_csv_to_db(csv_path)` | CSVファイルパス | 取り込み結果(成功件数/失敗件数) | CSVを読み込み型変換しMERGEで取り込み、ファイルを移動する |
| `merge_rows(rows)` | 変換済み行データ | なし（内部処理） | `Product_Number`+`Machine_Number`をキーにMERGE実行 |
| `move_processed_file(csv_path, success)` | CSVパス, 成否フラグ | なし | 成功時`データ転送後/`、失敗時`エラー項目/`へ移動 |

## UtilizationCalculator
| メソッド | 入力 | 出力 | 目的 |
|---|---|---|---|
| `get_daily_utilization(target_date)` | 対象日 | 号機別稼働率テーブル | 日別稼働率を算出 |
| `get_weekly_utilization(week_start)` | 週開始日 | 号機別 実績/想定稼働率テーブル | 週間稼働率・週間想定稼働率を算出 |
| `get_monthly_utilization(year, month)` | 年, 月 | 号機別稼働率テーブル | 月別稼働率を算出 |
| `get_planned_seconds(target_date)` | 対象日 | 計画時間(秒) | 曜日補正（日曜0/月曜9:00開始）を反映した計画時間を返す |

## DashboardApp
| メソッド | 入力 | 出力 | 目的 |
|---|---|---|---|
| `render_dashboard()` | なし | Streamlit画面 | ダッシュボード全体のレイアウトを描画するエントリーポイント |
| `render_daily_chart(daily_df)` | 日別稼働率データ | 折れ線グラフ | 号機別に色分けした日別稼働率グラフを描画 |
| `render_weekly_chart(weekly_df)` | 週別稼働率データ | 折れ線/棒グラフ | 実績（実線）と想定（破線）を重ねて描画 |
| `render_monthly_table(monthly_df)` | 月別稼働率データ | 表 | 月別稼働率の表を描画 |
| `render_machine_toggle_controls()` | なし | 選択中の号機リスト | 号機ごとの表示/非表示切替ボタンを描画 |

## SchedulingOrchestration
| メソッド | 入力 | 出力 | 目的 |
|---|---|---|---|
| `run_ingestion_pipeline()` | なし | 実行結果ログ | `CsvGenerator`→`DbLoader`を順に実行するエントリーポイント（スクリプト①） |
| `run_reporting_refresh()` | なし | 実行結果ログ | `UtilizationCalculator`の更新処理を実行するエントリーポイント（スクリプト②） |
