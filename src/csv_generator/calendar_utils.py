"""稼働カレンダー計算(BR-1, BR-2)。"""
from __future__ import annotations

from datetime import datetime, timedelta

from .config import BREAK_WINDOWS, MONDAY_NON_WORKING_END_HOUR
from .models import ExecutionWindow

WINDOW_HOURS = 12
SUNDAY_WEEKDAY = 6
MONDAY_WEEKDAY = 0


def resolve_execution_window(reference_time: datetime) -> ExecutionWindow:
    """reference_timeが属する12時間の実行窓(0-12時 or 12-24時)を求める(BR-1)。"""
    start_hour = 0 if reference_time.hour < 12 else 12
    window_start = reference_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(hours=WINDOW_HOURS)

    is_holiday = window_start.weekday() == SUNDAY_WEEKDAY
    monday_interval = _monday_non_working_interval(window_start, window_end)
    available_seconds = 0 if is_holiday else _compute_available_seconds(window_start, window_end, monday_interval)
    earliest_start = monday_interval[1] if monday_interval else window_start

    return ExecutionWindow(
        window_start=window_start,
        window_end=window_end,
        is_holiday=is_holiday,
        available_seconds=available_seconds,
        earliest_start=min(earliest_start, window_end),
    )


def is_within_break_time(moment: datetime) -> bool:
    """momentが休憩時間帯に含まれるか判定する。"""
    for start_h, start_m, end_h, end_m in BREAK_WINDOWS:
        break_start = moment.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        break_end = moment.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
        if break_start <= moment < break_end:
            return True
    return False


def _compute_available_seconds(
    window_start: datetime,
    window_end: datetime,
    monday_interval: tuple[datetime, datetime] | None,
) -> int:
    total_seconds = int((window_end - window_start).total_seconds())

    excluded_intervals = list(_break_time_intervals(window_start, window_end))
    if monday_interval is not None:
        excluded_intervals.append(monday_interval)

    excluded_seconds = _merge_and_sum_intervals(excluded_intervals)
    return max(total_seconds - excluded_seconds, 0)


def _monday_non_working_interval(
    window_start: datetime, window_end: datetime
) -> tuple[datetime, datetime] | None:
    """月曜 0:00-9:00 の非稼働時間と実行窓の重なり区間を返す(BR-1)。重なりがなければNone。"""
    if window_start.weekday() != MONDAY_WEEKDAY:
        return None
    non_working_end = window_start.replace(hour=MONDAY_NON_WORKING_END_HOUR, minute=0, second=0, microsecond=0)
    overlap_end = min(window_end, non_working_end)
    if overlap_end <= window_start:
        return None
    return (window_start, overlap_end)


def _break_time_intervals(window_start: datetime, window_end: datetime):
    """休憩時間帯と実行窓の重なり区間を列挙する(BR-2)。実行窓は同一日内に収まる(12時間単位)前提。"""
    target_day = window_start.date()
    for start_h, start_m, end_h, end_m in BREAK_WINDOWS:
        break_start = datetime.combine(target_day, datetime.min.time()).replace(hour=start_h, minute=start_m)
        break_end = datetime.combine(target_day, datetime.min.time()).replace(hour=end_h, minute=end_m)
        overlap_start = max(window_start, break_start)
        overlap_end = min(window_end, break_end)
        if overlap_end > overlap_start:
            yield (overlap_start, overlap_end)


def _merge_and_sum_intervals(intervals: list[tuple[datetime, datetime]]) -> int:
    """重複しうる区間をマージしてから合計秒数を求める(月曜非稼働と休憩時間の二重カウントを防ぐ)。"""
    if not intervals:
        return 0

    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]
    for start, end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    return sum(int((end - start).total_seconds()) for start, end in merged)
