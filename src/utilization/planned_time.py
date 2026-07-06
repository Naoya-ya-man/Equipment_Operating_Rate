"""計画時間(分母)の算出(BR-1)。"""
from __future__ import annotations

from datetime import date

from .config import DAY_SECONDS, MONDAY_NON_WORKING_SECONDS

SUNDAY_WEEKDAY = 6
MONDAY_WEEKDAY = 0


def get_planned_seconds(target_date: date) -> int:
    """対象日の計画時間(秒)を返す。日曜=0、月曜=86400-32400、その他=86400。"""
    weekday = target_date.weekday()
    if weekday == SUNDAY_WEEKDAY:
        return 0
    if weekday == MONDAY_WEEKDAY:
        return DAY_SECONDS - MONDAY_NON_WORKING_SECONDS
    return DAY_SECONDS
