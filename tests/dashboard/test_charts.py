from datetime import date

import pandas as pd

from src.dashboard.charts import build_daily_line_chart, build_weekly_combo_chart


def test_build_daily_line_chart_returns_empty_figure_for_empty_dataframe():
    figure = build_daily_line_chart(pd.DataFrame())
    assert len(figure.data) == 0


def test_build_daily_line_chart_creates_one_trace_per_series():
    df = pd.DataFrame(
        [
            {"target_date": date(2026, 7, 1), "series": "A-1", "machine_name": "A", "utilization_rate": 10.0},
            {"target_date": date(2026, 7, 2), "series": "A-1", "machine_name": "A", "utilization_rate": 20.0},
            {"target_date": date(2026, 7, 1), "series": "B-1", "machine_name": "B", "utilization_rate": 5.0},
        ]
    )

    figure = build_daily_line_chart(df)

    assert len(figure.data) == 2
    trace_names = {trace.name for trace in figure.data}
    assert trace_names == {"A-1", "B-1"}


def test_build_daily_line_chart_respects_selected_series():
    df = pd.DataFrame(
        [
            {"target_date": date(2026, 7, 1), "series": "A-1", "machine_name": "A", "utilization_rate": 10.0},
            {"target_date": date(2026, 7, 1), "series": "B-1", "machine_name": "B", "utilization_rate": 5.0},
        ]
    )

    figure = build_daily_line_chart(df, selected_series=["A-1"])

    assert len(figure.data) == 1
    assert figure.data[0].name == "A-1"


def test_build_weekly_combo_chart_creates_actual_and_expected_traces():
    df = pd.DataFrame(
        [
            {
                "week_start": date(2026, 7, 6),
                "series": "A-1",
                "machine_name": "A",
                "actual_rate": 10.0,
                "expected_rate": 20.0,
            }
        ]
    )

    figure = build_weekly_combo_chart(df)

    assert len(figure.data) == 2
    dash_styles = {trace.name: trace.line.dash for trace in figure.data}
    assert dash_styles["A-1(実績)"] == "solid"
    assert dash_styles["A-1(想定)"] == "dash"


def test_build_weekly_combo_chart_returns_empty_figure_for_empty_dataframe():
    figure = build_weekly_combo_chart(pd.DataFrame())
    assert len(figure.data) == 0
