# ビジネスロジックモデル（UOW-4: DashboardApp）

## 全体ワークフロー
```
1. ユーザーがUI上で以下を選択する:
   - 表示粒度(号機別/加工機タイプ別) (BR-1)
   - 各トレンドの表示期間 (BR-2〜BR-4)
   - 表示する系列(号機/加工機タイプ) (BR-5)

2. data_service.py が選択内容に応じてUtilizationCalculatorを繰り返し呼び出し、
   日別/週別/月別のトレンドDataFrameを構築する

3. charts.py がDataFrameからPlotly Figureを構築する
   - 日別: 折れ線グラフ、系列ごとに色分け (BR-8)
   - 週別: 実績(実線)+想定(破線)のコンボグラフ (BR-6)
   - 月別: 表(st.dataframe)

4. app.py がst.plotly_chart / st.dataframeで描画し、ホバーツールチップ(BR-7)を提供する
```

## データ整形（data_service.py）の責務
- `build_daily_trend(end_date, num_days, granularity) -> DataFrame`
- `build_weekly_trend(end_week_start, num_weeks, granularity) -> DataFrame`
- `build_monthly_trend(end_year, end_month, num_months, granularity) -> DataFrame`
- いずれも `UtilizationCalculator` を対象期間分繰り返し呼び出し、1つのDataFrameに積み上げる

## グラフ構築（charts.py）の責務
- `build_daily_line_chart(df, selected_series) -> plotly.graph_objects.Figure`
- `build_weekly_combo_chart(df, selected_series) -> plotly.graph_objects.Figure`
- 選択された系列(`selected_series`)のみを描画対象とする（BR-5）

## エラーハンドリング・エッジケース
- **データが空のDataFrame**: `charts.py` は空のFigureまたは警告メッセージ用のフラグを返し、`app.py` 側で `st.info("データがありません")` 等を表示する（BR-9）
- **DB接続不可**: `UtilizationCalculator`側の例外はそのまま伝播させ、`app.py`側で捕捉して `st.error()` でユーザーに通知する（アプリ全体をクラッシュさせない）

## パフォーマンス上の注意
- 各トレンド期間分、日次であれば最大60回、週次であれば最大26回のDBクエリが発生する。現状のデータ量では許容範囲内だが、将来的な最適化余地としてUOW-3のREADMEに記載済み
