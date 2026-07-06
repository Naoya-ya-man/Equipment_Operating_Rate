from datetime import date

from src.utilization.planned_time import get_planned_seconds


def test_sunday_planned_seconds_is_zero():
    sunday = date(2026, 7, 5)
    assert get_planned_seconds(sunday) == 0


def test_monday_planned_seconds_excludes_morning():
    monday = date(2026, 7, 6)
    assert get_planned_seconds(monday) == 86400 - 9 * 3600


def test_normal_weekday_planned_seconds_is_full_day():
    tuesday = date(2026, 7, 7)
    assert get_planned_seconds(tuesday) == 86400
