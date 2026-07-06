"""Streamlitダッシュボードのエントリーポイント(UOW-4: DashboardApp)。

実行方法: `streamlit run src/dashboard/app.py`

`streamlit run` はこのファイルを単独スクリプトとして実行するため、相対importは使えない
(「attempted relative import with no known parent package」で失敗する)。そのため、
ワークスペースルートをsys.pathに追加したうえで絶対importを行う。
"""
from __future__ import annotations

import sys
from datetime import date
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
from src.dashboard.data_service import build_daily_trend, build_monthly_trend, build_weekly_trend

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

except Exception as exc:  # noqa: BLE001 - アプリ全体のクラッシュを防ぎ、エラーをユーザーに通知する(BR-9関連)
    st.error(f"データの取得中にエラーが発生しました: {exc}")
