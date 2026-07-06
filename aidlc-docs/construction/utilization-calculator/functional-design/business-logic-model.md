# ビジネスロジックモデル（UOW-3: UtilizationCalculator）

## 全体ワークフロー（日別）
```
1. 対象日の計画時間(planned_seconds)を算出する (BR-1)
2. SSMSに対し、対象日のProcessing_Start_Timeでフィルタし、
   Machine_Name, Machine_Numberごとに Sum_DateTime を合計するクエリを実行する
3. 全25号機(A~E × 1~5)について、クエリ結果とマージし、
   データがない号機はactual_seconds=0とする (BR-7)
4. 各号機についてutilization_rateを算出する (BR-2)
5. UtilizationRowのリストを返す
```

## 全体ワークフロー（週別）
```
1. week_start(月曜日)から週末(日曜日)までの計画時間合計を算出する (BR-1, BR-3)
2. SSMSに対し、週範囲のProcessing_Start_Timeでフィルスし、
   Machine_Name, Machine_Numberごとに Sum_DateTime合計・件数(COUNT)を集計するクエリを実行する
3. 全25号機についてマージし、データがない号機は0とする (BR-7)
4. 各号機について actual_utilization_rate (BR-4) と expected_utilization_rate (BR-5) を算出する
5. WeeklyUtilizationRowのリストを返す
```

## 全体ワークフロー（月別）
```
1. 対象月の日数分、日別ワークフローを繰り返し実行する
2. 号機ごとにactual_seconds・planned_secondsを月内で合計する
3. utilization_rateを算出する (BR-6)
4. UtilizationRowのリストを返す
```

## クエリ設計
```sql
SELECT Machine_Name, Machine_Number, SUM(Sum_DateTime) AS actual_seconds, COUNT(*) AS processed_count
FROM [dbo].[A1_ProcessingMachine_Utilization_Rate]
WHERE Processing_Start_Time >= ? AND Processing_Start_Time < ?
GROUP BY Machine_Name, Machine_Number
```
- `(Machine_Name, Processing_Start_Time)` インデックス（UOW-2で作成済み）を活用する

## 入出力
- **入力**: 対象日/週(月曜日)/年月
- **出力**: 号機別(25件)の `UtilizationRow` または `WeeklyUtilizationRow` のリスト

## エラーハンドリング・エッジケース
- **日曜日の日別稼働率**: `planned_seconds=0` のため `utilization_rate=0.0` とする（ゼロ除算を回避）
- **データが1件もない期間**: 全25号機が `actual_seconds=0`, `utilization_rate=0.0` の行として返る（エラーにしない）

## 加工機タイプ単位への集計（BR-8）
号機ごとの `UtilizationRow` / `WeeklyUtilizationRow` のリストから、同一 `machine_name` の5号機分を合算して `MachineTypeUtilizationRow` / `MachineTypeWeeklyUtilizationRow` を導出する（追加のSQLクエリは不要、既存の号機別結果をPython側で集約するのみ）。

```
1. 号機別のUtilizationRow(25件)を取得する
2. machine_nameでグループ化し、actual_seconds・planned_secondsをそれぞれ合算する
3. utilization_rate = 合算actual_seconds / 合算planned_seconds * 100 を算出する
4. MachineTypeUtilizationRow(5件)を返す
```
週別も同様に、`processed_count` も合算したうえで `expected_utilization_rate` を算出する。
