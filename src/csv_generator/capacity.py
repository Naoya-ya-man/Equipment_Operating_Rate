"""理論生産数上限の計算(BR-3)。"""
from __future__ import annotations

import math

from .config import BOTTLENECK_MACHINE, STANDARD_MINUTES, UNIT_NUMBERS


def compute_window_capacity(available_seconds: int) -> int:
    """ボトルネック工程(既定: 加工機C)を基準にした、この実行窓における完成品数の理論上限。"""
    standard_seconds = STANDARD_MINUTES[BOTTLENECK_MACHINE] * 60
    if standard_seconds <= 0 or available_seconds <= 0:
        return 0
    unit_capacity = math.floor(available_seconds / standard_seconds)
    return unit_capacity * len(UNIT_NUMBERS)
