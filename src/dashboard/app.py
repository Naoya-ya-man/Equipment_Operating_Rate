"""Streamlitダッシュボードのエントリーポイント(UOW-4: DashboardApp)。

実行方法: `streamlit run src/dashboard/app.py`

`streamlit run` はこのファイルを単独スクリプトとして実行するため、相対importは使えない
(「attempted relative import with no known parent package」で失敗する)。そのため、
ワークスペースルートをsys.pathに追加したうえで絶対importを行う。
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[2])
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

import streamlit as st

from src.dashboard.charts import build_daily_line_chart, build_weekly_combo_chart
from src.dashboard.config import (
    DEFAULT_DAILY_DAYS,
    DEFAULT_MONTHLY_MONTHS,
    DEFAULT_WEEKLY_WEEKS,
    MAX_DAILY_DAYS,
    MAX_MONTHLY_MONTHS,
    MAX_WEEKLY_WEEKS,
    MIN_DAILY_DAYS,
    MIN_MONTHLY_MONTHS,
    MIN_WEEKLY_WEEKS,
)
from src.dashboard.data_service import (
    build_daily_comparison,
    build_daily_trend,
    build_monthly_comparison,
    build_monthly_trend,
    build_weekly_comparison,
    build_weekly_trend,
)

st.set_page_config(page_title="設備稼働率監視ボード", layout="wide")
st.title("設備稼働率監視ボード")

granularity_label = st.radio("表示粒度", ["号機別", "加工機タイプ別"], horizontal=True)
granularity = "unit" if granularity_label == "号機別" else "machine_type"

today = date.today()

try:
    daily_days = st.slider("日別トレンド期間(日)", MIN_DAILY_DAYS, MAX_DAILY_DAYS, DEFAULT_DAILY_DAYS)
    daily_df = build_daily_trend(today, daily_days, granularity)
    all_series = sorted(daily_df["series"].unique()) if not daily_df.empty else []
    selected_series = st.multiselect("表示する系列", all_series, default=all_series)

    st.subheader("日別稼働率")
    if daily_df.empty:
        st.info("データがありません")
    else:
        st.plotly_chart(build_daily_line_chart(daily_df, selected_series), width="stretch")

    weekly_weeks = st.slider("週別トレンド期間(週)", MIN_WEEKLY_WEEKS, MAX_WEEKLY_WEEKS, DEFAULT_WEEKLY_WEEKS)
    weekly_df = build_weekly_trend(today, weekly_weeks, granularity)
    st.subheader("週別稼働率(実績/想定)")
    if weekly_df.empty:
        st.info("データがありません")
    else:
        st.plotly_chart(build_weekly_combo_chart(weekly_df, selected_series), width="stretch")

    monthly_months = st.slider("月別トレンド期間(ヶ月)", MIN_MONTHLY_MONTHS, MAX_MONTHLY_MONTHS, DEFAULT_MONTHLY_MONTHS)
    monthly_df = build_monthly_trend(today, monthly_months, granularity)
    st.subheader("月別稼働率")
    if monthly_df.empty:
        st.info("データがありません")
    else:
        st.dataframe(monthly_df.pivot(index="year_month", columns="series", values="utilization_rate"))

    st.subheader("実績 vs 想定(理論値)の比較表")
    st.caption("想定(理論値) = 加工件数 × 標準加工時間 ÷ 計画時間 × 100。実績との差が大きい場合は生成量やデータ欠損を確認する目安になる。")
    period_label = st.radio("比較する期間", ["直近1日", "直近1週間", "直近1ヶ月"], horizontal=True)

    if period_label == "直近1日":
        comparison_df = build_daily_comparison(today, granularity)
    elif period_label == "直近1週間":
        comparison_df = build_weekly_comparison(today - timedelta(days=today.weekday()), granularity)
    else:
        comparison_df = build_monthly_comparison(today.year, today.month, granularity)

    if comparison_df.empty:
        st.info("データがありません")
    else:
        st.dataframe(
            comparison_df.rename(
                columns={
                    "series": "系列",
                    "processed_count": "加工件数",
                    "actual_rate": "実績稼働率(%)",
                    "expected_rate": "想定稼働率(%)",
                    "diff": "差分(実績-想定)",
                }
            ).drop(columns=["machine_name"]),
            hide_index=True,
        )

except Exception as exc:  # noqa: BLE001 - アプリ全体のクラッシュを防ぎ、エラーをユーザーに通知する(BR-9関連)
    st.error(f"データの取得中にエラーが発生しました: {exc}")
