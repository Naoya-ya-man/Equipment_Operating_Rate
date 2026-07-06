# ドメインエンティティ（UOW-3: UtilizationCalculator）

## MachineUnitKey（号機キー）
| 属性 | 型 | 説明 |
|---|---|---|
| machine_name | str | A〜E |
| machine_number | int | 1〜5 |

## UtilizationRow（日別・月別の稼働率行）
| 属性 | 型 | 説明 |
|---|---|---|
| machine_name | str | A〜E |
| machine_number | int | 1〜5 |
| actual_seconds | int | 実加工時間合計(秒) |
| planned_seconds | int | 計画時間(秒) |
| utilization_rate | float | 稼働率(%)。`planned_seconds=0`の場合は0.0 |

## WeeklyUtilizationRow（週別の稼働率行）
| 属性 | 型 | 説明 |
|---|---|---|
| machine_name | str | A〜E |
| machine_number | int | 1〜5 |
| actual_seconds | int | 週間の実加工時間合計(秒) |
| planned_seconds | int | 週間の計画時間合計(秒) |
| processed_count | int | 週間の加工件数（想定稼働率の算出に使用） |
| actual_utilization_rate | float | 週間稼働率(%) |
| expected_utilization_rate | float | 週間想定稼働率(%) |

## MachineTypeUtilizationRow（加工機タイプ単位・日別/月別の稼働率行）
号機(1〜5)を合算した、加工機タイプ(A〜E)単位の集計行。
| 属性 | 型 | 説明 |
|---|---|---|
| machine_name | str | A〜E |
| actual_seconds | int | 5号機分の実加工時間合計(秒) |
| planned_seconds | int | 5号機分の計画時間合計(秒) |
| utilization_rate | float | 稼働率(%) |

## MachineTypeWeeklyUtilizationRow（加工機タイプ単位・週別の稼働率行）
| 属性 | 型 | 説明 |
|---|---|---|
| machine_name | str | A〜E |
| actual_seconds | int | 5号機分の週間実加工時間合計(秒) |
| planned_seconds | int | 5号機分の週間計画時間合計(秒) |
| processed_count | int | 5号機分の週間加工件数合計 |
| actual_utilization_rate | float | 週間稼働率(%) |
| expected_utilization_rate | float | 週間想定稼働率(%) |

## 関係
- `UtilizationRow` / `WeeklyUtilizationRow` は、加工機タイプ(A〜E) × 号機(1〜5) = 25通りの `MachineUnitKey` それぞれについて1行ずつ生成する（データが存在しない号機も0として含める）
- 月別集計は日別の `UtilizationRow` を対象月の日数分積み上げて算出する
- `MachineTypeUtilizationRow` / `MachineTypeWeeklyUtilizationRow` は、同一 `machine_name` の5号機分の `UtilizationRow` / `WeeklyUtilizationRow` を合算して導出する（BR-8）
