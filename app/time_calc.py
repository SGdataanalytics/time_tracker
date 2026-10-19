"""
Presentation-layer time calculations for time_tracker.

`duration_minutes` is the canonical measure of time spent (see "Phase 1
architecture decisions" in PROJECT.md). `start_time` and `end_time` are
optional, secondary fields that are never required to make the duration
meaningful.

This module adds one small, pure helper: deriving a display-only end time
from `start_time` + `duration_minutes` when the user has supplied a start
time but left end_time blank. It does not read or write the database and
has no Flask dependency, so it is trivial to unit-test in isolation (see
tests/test_time_calc.py).

Important: this is presentation-only. The derived value is never written
back to the database — `end_time` in storage remains exactly what the user
typed (or NULL if they left it blank).
"""

from datetime import datetime, timedelta

_TIME_FORMAT = "%H:%M"
_MINUTES_PER_DAY = 24 * 60


def derive_end_time(start_time, duration_minutes):
    """Return an "HH:MM" end time derived from start_time + duration_minutes.

    - Returns None if `start_time` is missing/blank or `duration_minutes`
      is missing, so callers can fall back to "no end time to show".
    - Wraps correctly past midnight, e.g. "23:30" + 120 minutes -> "01:30".
    - Does not touch the database; this is a pure, presentation-only
      calculation meant to be called from routes.py when rendering pages.
    """
    if not start_time or duration_minutes is None:
        return None

    try:
        start = datetime.strptime(start_time, _TIME_FORMAT)
    except ValueError:
        # Malformed start_time (should not normally happen, since the form
        # uses <input type="time">) — fail safe by showing nothing derived.
        return None

    end = start + timedelta(minutes=duration_minutes)
    # Normalize back onto a single HH:MM clock face, wrapping past midnight
    # (and past multiple days, for unusually long durations) using modulo
    # arithmetic on minutes-since-midnight.
    total_minutes = (end.hour * 60 + end.minute) % _MINUTES_PER_DAY
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def display_end_time(start_time, end_time, duration_minutes):
    """Return the end time to display for an entry.

    - If the user explicitly entered an end_time, that explicit value is
      returned as-is (it always takes priority).
    - Otherwise, if start_time is present, an end time is derived from
      start_time + duration_minutes for display purposes only.
    - Otherwise, returns None (nothing to show).
    """
    if end_time:
        return end_time
    return derive_end_time(start_time, duration_minutes)
