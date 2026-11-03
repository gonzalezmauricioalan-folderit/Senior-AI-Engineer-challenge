from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.domain.detection import N_WEEKS
from app.domain.weeks import (
    first_complete_week,
    history,
    latest_complete_week,
    local_date,
    series_start,
    weekly_counts,
)

CHICAGO = ZoneInfo("America/Chicago")


def test_first_complete_week_monday_vs_midweek():
    assert first_complete_week(date(2026, 2, 2)) == date(2026, 2, 2)  # Monday: that week is whole
    assert first_complete_week(date(2026, 2, 1)) == date(2026, 2, 2)  # Sunday: next Monday
    assert first_complete_week(date(2026, 2, 4)) == date(2026, 2, 9)  # Wednesday: skip the partial week


def test_latest_complete_week_monday_vs_sunday():
    assert latest_complete_week(date(2026, 7, 27)) == date(2026, 7, 20)  # Monday
    assert latest_complete_week(date(2026, 7, 26)) == date(2026, 7, 13)  # Sunday: its week isn't over


def test_local_date_across_dst_switch():
    # US DST starts 2026-03-08 02:00 local. Same UTC wall time maps to UTC-6 before, UTC-5 after.
    assert local_date(datetime(2026, 3, 8, 5, 59), CHICAGO) == date(2026, 3, 7)  # 23:59 CST
    assert local_date(datetime(2026, 3, 8, 6, 0), CHICAGO) == date(2026, 3, 8)  # 00:00 CST
    assert local_date(datetime(2026, 3, 9, 4, 59), CHICAGO) == date(2026, 3, 8)  # 23:59 CDT
    assert local_date(datetime(2026, 3, 9, 5, 0), CHICAGO) == date(2026, 3, 9)  # 00:00 CDT


def test_weekly_counts_buckets_by_local_monday():
    # Sun 23:30 local is already Mon in UTC, but belongs to the previous local week.
    counts = weekly_counts([datetime(2026, 7, 27, 4, 30), datetime(2026, 7, 27, 6, 0)], CHICAGO)
    assert counts == {date(2026, 7, 20): 1, date(2026, 7, 27): 1}


def test_series_start_and_history_zero_fill():
    counts = {date(2026, 6, 1): 2, date(2026, 6, 15): 5}
    assert series_start(counts, date(2026, 6, 8)) == date(2026, 6, 15)
    assert series_start(counts, date(2026, 6, 16)) is None
    week = date(2026, 6, 29)
    assert history(counts, date(2026, 6, 1), week, 8) == [
        (date(2026, 6, 1), 2),
        (date(2026, 6, 8), 0),
        (date(2026, 6, 15), 5),
        (date(2026, 6, 22), 0),
    ]
    assert history(counts, None, week, 8) == []
    assert history(counts, week, week, 8) == []  # series starts at the week itself: no history
    # Window is capped at 8 weeks and excludes the evaluated week.
    h = history({}, date(2026, 1, 5), date(2026, 7, 20), 8)
    assert len(h) == 8
    assert h[0][0] == date(2026, 5, 25)
    assert h[-1][0] == date(2026, 7, 13)


def test_series_start_includes_first_week_itself():
    assert series_start({date(2026, 2, 2): 1}, date(2026, 2, 2)) == date(2026, 2, 2)


def test_history_is_capped_at_n_weeks():
    week = date(2026, 7, 20)
    counts = {week - timedelta(days=7 * i): i for i in range(1, 13)}  # 12 weeks of data, count = distance
    h = history(counts, week - timedelta(days=7 * 12), week, N_WEEKS)
    assert [n for _, n in h] == [8, 7, 6, 5, 4, 3, 2, 1]  # oldest kept is 8 weeks back, W itself absent
