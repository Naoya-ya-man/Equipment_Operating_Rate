"""ダッシュボードの設定値・配色(BR-8)。"""
from __future__ import annotations

from typing import Optional

BASE_COLORS = {
    "A": "#1f77b4",  # 青
    "B": "#2ca02c",  # 緑
    "C": "#ff7f0e",  # オレンジ
    "D": "#d62728",  # 赤
    "E": "#9467bd",  # 紫
}

DEFAULT_DAILY_DAYS = 14
DEFAULT_WEEKLY_WEEKS = 8
DEFAULT_MONTHLY_MONTHS = 6

MIN_DAILY_DAYS, MAX_DAILY_DAYS = 7, 60
MIN_WEEKLY_WEEKS, MAX_WEEKLY_WEEKS = 4, 26
MIN_MONTHLY_MONTHS, MAX_MONTHLY_MONTHS = 3, 24

_UNIT_SHADE_FACTORS = {1: 1.0, 2: 0.85, 3: 0.7, 4: 0.55, 5: 0.4}


def color_for_series(machine_name: str, series: str) -> str:
    """加工機タイプごとの基準色を返す。号機別表示の場合は号機番号に応じて濃淡を変える。"""
    base_color = BASE_COLORS[machine_name]
    unit_number = _extract_unit_number(series)
    if unit_number is None:
        return base_color
    factor = _UNIT_SHADE_FACTORS.get(unit_number, 1.0)
    return _shade(base_color, factor)


def _extract_unit_number(series: str) -> Optional[int]:
    if "-" not in series:
        return None
    _, _, suffix = series.partition("-")
    return int(suffix) if suffix.isdigit() else None


def _shade(hex_color: str, factor: float) -> str:
    """hex_colorの明度をfactor倍にした色を返す(1.0=そのまま、値が小さいほど暗くなる)。"""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    shaded = (max(0, min(255, int(channel * factor))) for channel in (r, g, b))
    return "#{:02x}{:02x}{:02x}".format(*shaded)
