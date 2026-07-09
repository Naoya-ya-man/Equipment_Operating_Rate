# ビジネスルール（UOW-3: UtilizationCalculator）

## BR-1: 計画時間（分母）の算出
- 基本は86400秒/日（三交代制、24時間）
- 日曜日: 計画時間0秒（全休）
- 月曜日: 86400秒 - 32400秒(0:00-9:00) = 54000秒
- 休憩時間帯はCsvGenerator側の生成可否には影響するが、稼働率の計画時間（分母）からは減算しない（`requirements.md` FR-3の式に準拠し、要件定義に明記された86400秒ベースの式をそのまま用いる）

## BR-2: 日別稼働率
- 対象日の `[Processing_Start_Time が対象日]` のレコードを号機ごとに集計し、`Sum_DateTime` の合計を実加工時間(秒)とする
- 【2026-07-09追加】日別・月別についても、週別(BR-5)と同様に想定稼働率（加工件数×標準加工時間÷計画時間×100）を算出し、`UtilizationRow`に`processed_count`/`expected_utilization_rate`として持たせる。実績と想定を比較できるようにするため（ダッシュボードの比較表で使用）
- `utilization_rate = actual_seconds / planned_seconds * 100`（`planned_seconds = 0` の場合は0.0とする、日曜日等）
- 加工機タイプ(A〜E) × 号機(1〜5) = 25通り全てについて行を生成する（データがない号機は `actual_seconds = 0`）

## BR-3: 週の起算日（ユーザー確認済み）
- 「週」は**月曜日始まり〜日曜日終わり**のISO週とする
- `get_weekly_utilization(week_start)` の `week_start` は月曜日の日付を受け取る想定とする

## BR-4: 週間稼働率
- 週内（月〜日）の日別実加工時間・計画時間をそれぞれ合計する
- `actual_utilization_rate = 週合計actual_seconds / 週合計planned_seconds * 100`

## BR-5: 週間想定稼働率
- 週内の号機ごとの加工件数(`processed_count`、レコード数)を集計する
- `expected_utilization_rate = (processed_count × 標準加工時間(秒)) / 週合計planned_seconds * 100`
- 標準加工時間はCsvGeneratorの基準値（A=20分, B=30分, C=40分, D=25分, E=15分）を参照する

## BR-6: 月別稼働率
- 対象月の全日について日別集計（BR-2）を行い、実加工時間・計画時間をそれぞれ合計する
- `utilization_rate = 月合計actual_seconds / 月合計planned_seconds * 100`

## BR-7: データが存在しない期間の扱い
- クエリ結果に現れない号機（その期間に一切加工実績がない）は `actual_seconds = 0`, `processed_count = 0` として結果に含める（ダッシュボードで全25号機を一貫して表示するため）

## BR-8: 加工機タイプ単位の集計（号機ごと・加工機ごと両方の粒度を提供）
- ユーザー要望により、号機(1〜5)ごとの粒度に加えて、加工機タイプ(A〜E)単位で5号機分を合算した集計も提供する
- `machine_type_actual_seconds = Σ(該当タイプの5号機分のactual_seconds)`
- `machine_type_planned_seconds = Σ(該当タイプの5号機分のplanned_seconds)`（日別/月別では日ごとの計画時間 × 5号機分、週別では週間計画時間 × 5号機分に相当）
- `machine_type_utilization_rate = machine_type_actual_seconds / machine_type_planned_seconds * 100`
- 週間想定稼働率も同様に、5号機分の `processed_count` を合算してから算出する
- 日別・週別・月別のいずれの粒度でも、号機別（25行）と加工機タイプ別（5行）の両方を算出できるようにする
