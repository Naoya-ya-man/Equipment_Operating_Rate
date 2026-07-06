# ドメインエンティティ（UOW-4: DashboardApp）

## Granularity（表示粒度）
`"unit"`（号機別、25系列） または `"machine_type"`（加工機タイプ別、5系列）のいずれか。UOW-3のBR-8対応（ユーザー要望）をUI上で切り替え可能にする。

## DailyTrendPoint（日別トレンドの1点）
| 属性 | 型 | 説明 |
|---|---|---|
| target_date | date | 対象日 |
| series | str | 系列名（`"A-1"` または `"A"`、granularityによる） |
| machine_name | str | A〜E |
| utilization_rate | float | 稼働率(%) |

## WeeklyTrendPoint（週別トレンドの1点）
| 属性 | 型 | 説明 |
|---|---|---|
| week_start | date | 週の開始日（月曜） |
| series | str | 系列名 |
| machine_name | str | A〜E |
| actual_rate | float | 週間稼働率(%) |
| expected_rate | float | 週間想定稼働率(%) |

## MonthlyTrendPoint（月別トレンドの1点）
| 属性 | 型 | 説明 |
|---|---|---|
| year | int | 年 |
| month | int | 月 |
| series | str | 系列名 |
| machine_name | str | A〜E |
| utilization_rate | float | 稼働率(%) |

## 関係
- 各TrendPointはpandas DataFrameの1行に対応する
- `series` は Plotlyの凡例・色分けのキーとして使用する（UOW-3の`UtilizationRow`等を、対象期間分繰り返し取得して積み上げる）
