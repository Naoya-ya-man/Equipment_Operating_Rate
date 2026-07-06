# ドメインエンティティ（UOW-2: DbLoader）

## DbRecord（DB投入用レコード）
CSVの1行を型変換した結果。SSMSのカラム型に合わせる。
| 属性 | 型 | 備考 |
|---|---|---|
| product_number | str | VARCHAR(50) |
| machine_name | str | VARCHAR(50) |
| machine_number | str | VARCHAR(50)（CSV上はint、DBカラム定義がVARCHARのため文字列変換） |
| processing_start_time | datetime | DATETIME |
| processing_completion_time | datetime | DATETIME |
| sum_datetime | int | INT |
| pass_judgment | str | VARCHAR(50)（"OK"/"NG"） |

## LoadResult（取り込み結果）
| 属性 | 型 | 備考 |
|---|---|---|
| file_path | Path | 対象CSVファイル |
| success | bool | 取り込み成功可否 |
| row_count | int | 取り込んだ行数（失敗時は0） |
| error_message | str \| None | 失敗時のエラー内容 |

## 関係
- 1つのCSVファイル → N件の `DbRecord` → 1件の `LoadResult`
- `DbRecord` はSSMSテーブル `[dbo].[A1_ProcessingMachine_Utilization_Rate]` の1行に対応
