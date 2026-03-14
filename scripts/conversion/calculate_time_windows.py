#!/usr/bin/env python3
"""
Time window calculator for home care recurring visits.

Calculates minStartTime, maxStartTime, maxEndTime in ISO 8601 format for:
- Daily visits: narrow window using flex_beforeStart, flex_afterStart, date from row index
- Weekly/biweekly/3weekly/4weekly/monthly: full period span (07:00 to 22:00)

Planning window: Monday 2026-02-16 07:00 to Sunday 2026-03-01 22:00 (2 weeks).
Timezone: Europe/Stockholm (+01:00 in February).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

# Planning window constants
PLANNING_START_DATE = "2026-02-16"
TIMEZONE_SUFFIX = "+01:00"
DAY_START = "07:00"
DAY_END = "22:00"


def _parse_time_minutes(time_str: str) -> int:
    """Parse HH:MM or HH:MM:SS to minutes since midnight."""
    if not time_str or not isinstance(time_str, str):
        return 0
    try:
        parts = time_str.strip().split(":")
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        return h * 60 + m
    except (ValueError, IndexError):
        return 0


def _to_iso_datetime(date_str: str, time_str: str) -> str:
    """Combine date (YYYY-MM-DD) and time (HH:MM) into ISO 8601 string."""
    base = datetime.fromisoformat(date_str)
    minutes = _parse_time_minutes(time_str)
    dt = base.replace(hour=minutes // 60, minute=minutes % 60, second=0, microsecond=0)
    return dt.isoformat() + TIMEZONE_SUFFIX


def _parse_int(val: Any, default: int = 0) -> int:
    """Safely parse integer from string or number."""
    if val is None or val == "":
        return default
    try:
        return int(float(str(val).replace(",", ".")))
    except (ValueError, TypeError):
        return default


def calculate_time_windows_daily(
    row: Dict[str, Any],
    visit_date: datetime,
) -> Tuple[str, str, str]:
    """
    Calculate time windows for a daily visit (specific date, narrow window).

    minStartTime = date + startTime - flex_beforeStart
    maxStartTime = date + startTime + flex_afterStart
    maxEndTime = maxStartTime + duration

    Args:
        row: CSV row with startTime, duration, flex_beforeStart, flex_afterStart
        visit_date: The specific date for this visit (datetime, no time)

    Returns:
        (minStartTime, maxStartTime, maxEndTime) as ISO 8601 strings
    """
    start_time = str(row.get("startTime", "07:00")).strip()
    duration = _parse_int(row.get("duration", 0))
    flex_before = _parse_int(row.get("flex_beforeStart", 0))
    flex_after = _parse_int(row.get("flex_afterStart", 0))

    start_minutes = _parse_time_minutes(start_time)
    base_dt = visit_date.replace(
        hour=start_minutes // 60,
        minute=start_minutes % 60,
        second=0,
        microsecond=0,
    )

    min_start_dt = base_dt - timedelta(minutes=flex_before)
    max_start_dt = base_dt + timedelta(minutes=flex_after)
    max_end_dt = max_start_dt + timedelta(minutes=duration)

    min_start_str = min_start_dt.isoformat() + TIMEZONE_SUFFIX
    max_start_str = max_start_dt.isoformat() + TIMEZONE_SUFFIX
    max_end_str = max_end_dt.isoformat() + TIMEZONE_SUFFIX

    return (min_start_str, max_start_str, max_end_str)


def calculate_time_windows_period(
    planning_start: datetime,
    week_number: int,
    period_weeks: int,
) -> Tuple[str, str]:
    """
    Calculate time windows for weekly/biweekly/3weekly/4weekly/monthly (full period span).

    minStartTime = first day of period at 07:00
    maxEndTime = last day of period at 22:00

    Args:
        planning_start: Monday of week 0 (07:00)
        week_number: 0, 1, 2, 3
        period_weeks: 1 for weekly, 2 for biweekly, 3 for 3weekly, 4 for 4weekly/monthly

    Returns:
        (minStartTime, maxEndTime) as ISO 8601 strings
    """
    period_start = planning_start + timedelta(weeks=week_number)
    period_start = period_start.replace(hour=7, minute=0, second=0, microsecond=0)

    period_end = period_start + timedelta(weeks=period_weeks, days=-1)
    period_end = period_end.replace(hour=22, minute=0, second=0, microsecond=0)

    min_start_str = period_start.isoformat() + TIMEZONE_SUFFIX
    max_end_str = period_end.isoformat() + TIMEZONE_SUFFIX

    return (min_start_str, max_end_str)


def get_visit_date_from_weekday_index(
    planning_start: datetime,
    weekday_index: int,
    week_number: int,
) -> datetime:
    """
    Get visit date from weekday index (0=Mon, 6=Sun) and week number.

    Args:
        planning_start: Monday of week 0
        weekday_index: 0-6 (Mon-Sun)
        week_number: 0, 1, 2, 3

    Returns:
        datetime for that date (time set to midnight for date-only use)
    """
    visit_date = planning_start + timedelta(weeks=week_number, days=weekday_index)
    return visit_date.replace(hour=0, minute=0, second=0, microsecond=0)
