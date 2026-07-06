"""Plotly Figureの構築(UOW-4: DashboardApp)。"""
from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.graph_objects as go

from .config import color_for_series


def build_daily_line_chart(df: pd.DataFrame, selected_series: Optional[list[str]] = None) -> go.Figure:
    """日別稼働率の折れ線グラフを構築する(BR-8: 加工機タイプごとの色分け)。"""
    figure = go.Figure()
    if df.empty:
        return figure

    for series in _resolve_series(df, selected_series):
        series_df = df[df["series"] == series].sort_values("target_date")
        if series_df.empty:
            continue
        color = color_for_series(series_df["machine_name"].iloc[0], series)
        figure.add_trace(
            go.Scatter(
                x=series_df["target_date"],
                y=series_df["utilization_rate"],
                mode="lines+markers",
                name=series,
                line=dict(color=color),
                hovertemplate=f"%{{x}}<br>{series}: %{{y:.2f}}%<extra></extra>",
            )
        )

    figure.update_layout(yaxis_title="稼働率(%)", xaxis_title="日付", legend_title="系列")
    return figure


def build_weekly_combo_chart(df: pd.DataFrame, selected_series: Optional[list[str]] = None) -> go.Figure:
    """週別稼働率の実績(実線)+想定(破線)コンボグラフを構築する(BR-6)。"""
    figure = go.Figure()
    if df.empty:
        return figure

    for series in _resolve_series(df, selected_series):
        series_df = df[df["series"] == series].sort_values("week_start")
        if series_df.empty:
            continue
        color = color_for_series(series_df["machine_name"].iloc[0], series)

        figure.add_trace(
            go.Scatter(
                x=series_df["week_start"],
                y=series_df["actual_rate"],
                mode="lines+markers",
                name=f"{series}(実績)",
                line=dict(color=color, dash="solid"),
                hovertemplate=f"%{{x}}<br>{series} 実績: %{{y:.2f}}%<extra></extra>",
            )
        )
        figure.add_trace(
            go.Scatter(
                x=series_df["week_start"],
                y=series_df["expected_rate"],
                mode="lines",
                name=f"{series}(想定)",
                line=dict(color=color, dash="dash"),
                hovertemplate=f"%{{x}}<br>{series} 想定: %{{y:.2f}}%<extra></extra>",
            )
        )

    figure.update_layout(yaxis_title="稼働率(%)", xaxis_title="週開始日(月曜)", legend_title="系列")
    return figure


def _resolve_series(df: pd.DataFrame, selected_series: Optional[list[str]]) -> list[str]:
    if selected_series is not None:
        return selected_series
    return sorted(df["series"].unique())
