from datetime import datetime

from src.csv_generator.calendar_utils import is_within_break_time, resolve_execution_window


def test_sunday_window_is_holiday_with_zero_available_seconds():
    sunday_morning = datetime(2026, 7, 5, 3, 0)  # 2026-07-05は日曜日
    window = resolve_execution_window(sunday_morning)

    assert window.is_holiday is True
    assert window.available_seconds == 0


def test_monday_morning_window_excludes_non_working_hours_and_breaks():
    monday_morning = datetime(2026, 7, 6, 3, 0)  # 2026-07-06は月曜日
    window = resolve_execution_window(monday_morning)

    # 窓(0-12時) - 非稼働(0-9時, 32400秒) - 休憩(10:00-10:20, 1200秒) = 9600秒
    # 2:00-2:45, 5:00-5:15の休憩は0-9時の非稼働時間に含まれるため二重に減算しない
    assert window.is_holiday is False
    assert window.available_seconds == 9600
    assert window.earliest_start == datetime(2026, 7, 6, 9, 0)


def test_normal_weekday_window_excludes_only_break_time():
    tuesday_morning = datetime(2026, 7, 7, 1, 0)  # 2026-07-07は火曜日
    window = resolve_execution_window(tuesday_morning)

    # 窓(0-12時) - 休憩(2:00-2:45=2700秒, 5:00-5:15=900秒, 10:00-10:20=1200秒) = 43200-4800=38400秒
    assert window.available_seconds == 38400


def test_is_within_break_time_detects_break_window():
    during_lunch_break = datetime(2026, 7, 7, 12, 30)
    outside_break = datetime(2026, 7, 7, 14, 0)

    assert is_within_break_time(during_lunch_break) is True
    assert is_within_break_time(outside_break) is False
