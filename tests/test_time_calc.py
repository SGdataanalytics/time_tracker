"""
Unit tests for app/time_calc.py (derived end-time display).

Uses Python's built-in `unittest`, consistent with the project's "keep
dependencies minimal" principle (Flask is the only direct dependency;
no test framework is added for this small, pure-function module).

Run with:
    .venv/bin/python -m unittest tests/test_time_calc.py -v
or:
    .venv/bin/python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

# Allow running this file directly (`python tests/test_time_calc.py`)
# without having the project installed as a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.time_calc import derive_end_time, display_end_time


class DeriveEndTimeTests(unittest.TestCase):
    def test_simple_same_day(self):
        self.assertEqual(derive_end_time("09:00", 30), "09:30")

    def test_crosses_hour_boundary(self):
        self.assertEqual(derive_end_time("09:45", 30), "10:15")

    def test_crosses_midnight(self):
        # The exact scenario named in the requirements.
        self.assertEqual(derive_end_time("23:30", 120), "01:30")

    def test_ends_exactly_at_midnight(self):
        self.assertEqual(derive_end_time("23:00", 60), "00:00")

    def test_zero_duration_returns_start_time(self):
        self.assertEqual(derive_end_time("10:00", 0), "10:00")

    def test_duration_longer_than_a_day_wraps_correctly(self):
        # 25 hours after 10:00 is 11:00 the next day; on a single HH:MM
        # clock face that is displayed as "11:00".
        self.assertEqual(derive_end_time("10:00", 25 * 60), "11:00")

    def test_missing_start_time_returns_none(self):
        self.assertIsNone(derive_end_time(None, 30))
        self.assertIsNone(derive_end_time("", 30))

    def test_missing_duration_returns_none(self):
        self.assertIsNone(derive_end_time("09:00", None))

    def test_malformed_start_time_returns_none(self):
        self.assertIsNone(derive_end_time("not-a-time", 30))


class DisplayEndTimeTests(unittest.TestCase):
    def test_explicit_end_time_takes_priority(self):
        # Even though start_time + duration would derive "09:30", the
        # user's explicit "10:00" must win.
        self.assertEqual(display_end_time("09:00", "10:00", 30), "10:00")

    def test_derives_when_end_time_blank(self):
        self.assertEqual(display_end_time("09:00", None, 30), "09:30")
        self.assertEqual(display_end_time("09:00", "", 30), "09:30")

    def test_crosses_midnight_when_derived(self):
        self.assertEqual(display_end_time("23:30", None, 120), "01:30")

    def test_no_start_time_and_no_end_time_returns_none(self):
        self.assertIsNone(display_end_time(None, None, 30))

    def test_no_start_time_but_explicit_end_time_returns_explicit(self):
        # Edge case: end_time without start_time is unusual but should
        # still just be displayed as entered, with no derivation attempted.
        self.assertEqual(display_end_time(None, "11:00", 30), "11:00")


if __name__ == "__main__":
    unittest.main()
