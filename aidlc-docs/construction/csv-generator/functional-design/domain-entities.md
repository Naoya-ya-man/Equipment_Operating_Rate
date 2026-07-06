# ドメインエンティティ（UOW-1: CsvGenerator）

## ExecutionWindow（実行窓）
1回のGitHub Actions実行（12時間ごと）が対象とする時間帯。
| 属性 | 型 | 説明 |
|---|---|---|
| window_start | datetime | この実行窓の開始時刻 |
| window_end | datetime | この実行窓の終了時刻（window_start + 12時間） |
| is_holiday | bool | 窓の属する日が日曜日か（全休） |
| is_monday_morning_affected | bool | 窓が月曜0:00〜9:00を含むか |
| available_seconds | int | 休憩時間・非稼働時間を除いたこの窓内の稼働可能秒数 |

## MachineType（加工機タイプ）
A/B/C/D/Eのいずれか。標準加工時間を持つ。
| 属性 | 型 | 説明 |
|---|---|---|
| name | str | "A"〜"E" |
| standard_minutes | int | 標準加工時間（A=20, B=30, C=40, D=25, E=15） |
| is_bottleneck | bool | 理論生産数算出の基準工程か（基準値ではC） |

## MachineUnit（号機）
| 属性 | 型 | 説明 |
|---|---|---|
| machine_type | MachineType | 所属する加工機タイプ |
| unit_number | int | 1〜5 |
| assignment_count | int | この窓内での割当回数（均等配分の判定に使用） |

## ProductChain（製品チェーン）
1つの製品がA→B→C→D→Eの5工程を通過する一連の処理。
| 属性 | 型 | 説明 |
|---|---|---|
| base_product_id | str | 品番ベース（6桁） |
| stages | list[ProcessingRecord] | A〜E、5件のレコード（工程順） |
| is_completed | bool | Eまで完了したか（完成品かどうか） |

## ProcessingRecord（加工実績レコード）
CSVの1行・DBの1レコードに対応。
| 属性 | 型 | 説明 |
|---|---|---|
| product_number | str | 7桁（先頭6桁=base_product_id, 末尾1桁=machine_type） |
| machine_name | str | A〜E |
| machine_number | int | 1〜5（号機） |
| processing_start_time | datetime | 開始時刻 |
| processing_completion_time | datetime | 終了時刻 |
| sum_datetime | int | 加工時間（秒、start〜completionの差分） |
| pass_judgment | str | "OK" または "NG" |
| had_breakdown | bool | 設備停止相当（2〜3倍時間）が発生したか（内部フラグ、CSV出力はしない） |

## 関係
- 1 `ExecutionWindow` に対して、N件の `ProductChain` が生成される
- 1 `ProductChain` は必ず5件の `ProcessingRecord`（A, B, C, D, E各1件）から成る
- 各 `ProcessingRecord` は1つの `MachineUnit` に割り当てられる
