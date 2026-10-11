# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the questions the engine asks of the diary, and its writes.

An engine on a diary in memory, with readings made up by the test.
"""

import datetime
import os
import sqlite3
import unittest

from engine import Engine
from log import Log

SEATED = 1
LYING = 2

OCTOBER = (datetime.date(2026, 10, 1), datetime.date(2026, 10, 31))


class DiaryTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = Engine(":memory:", Log(os.devnull))

    def tearDown(self):
        self.engine.db.close()

    def add(self, recorded_at, systolic, diastolic, rate=70,
            position=SEATED):
        values = self.engine.get_reading_values(recorded_at, position,
                                                systolic, diastolic, rate)
        return self.engine.add_reading(values)

    def test_readings_of_the_period_latest_first(self):
        self.add("2026-10-01 08:00:00", 120, 80)
        self.add("2026-10-02 08:00:00", 130, 82)
        rows = self.engine.get_readings(*OCTOBER)
        self.assertEqual([row["recorded_at"] for row in rows],
                         ["2026-10-02 08:00:00", "2026-10-01 08:00:00"])

    def test_last_second_of_the_period_is_inside(self):
        self.add("2026-10-31 23:59:59", 120, 80)
        self.assertEqual(len(self.engine.get_readings(*OCTOBER)), 1)

    def test_day_after_the_period_is_outside(self):
        self.add("2026-11-01 00:00:00", 120, 80)
        self.assertEqual(self.engine.get_readings(*OCTOBER), [])

    def test_statistics_are_per_position(self):
        self.add("2026-10-01 08:00:00", 120, 80, 60)
        self.add("2026-10-01 08:01:00", 130, 90, 70)
        self.add("2026-10-01 21:00:00", 110, 70, 58, LYING)
        rows = self.engine.get_statistics(*OCTOBER)
        seated, lying = rows
        self.assertEqual((seated["position"], seated["readings"]),
                         ("seated", 2))
        self.assertEqual((seated["systolic_mean"], seated["systolic_min"],
                          seated["systolic_max"]), (125.0, 120, 130))
        self.assertEqual(seated["heart_rate_mean"], 65.0)
        self.assertEqual((lying["position"], lying["readings"]),
                         ("lying", 1))

    def test_position_without_readings_has_no_row(self):
        self.add("2026-10-01 08:00:00", 120, 80)
        rows = self.engine.get_statistics(*OCTOBER)
        self.assertEqual([row["position"] for row in rows], ["seated"])

    def test_no_readings_no_statistics(self):
        self.assertEqual(self.engine.get_statistics(*OCTOBER), [])

    def test_correction_replaces_the_reading(self):
        old_id = self.add("2026-10-01 08:00:00", 210, 80)
        values = self.engine.get_reading_values("2026-10-01 08:00:00",
                                                SEATED, 120, 80, 70)
        new_id = self.engine.correct_reading(old_id, values)
        rows = self.engine.get_readings(*OCTOBER)
        self.assertEqual([row["reading_id"] for row in rows], [new_id])
        self.assertEqual(rows[0]["systolic_mmhg"], 120)
        self.assertEqual(self.engine.get_reading(old_id)["enable"], 0)

    def test_failed_correction_leaves_the_old_reading(self):
        old_id = self.add("2026-10-01 08:00:00", 120, 80)
        bad = self.engine.get_reading_values("2026-10-01 08:00:00",
                                             SEATED, 70, 80, 70)
        with self.assertRaises(sqlite3.IntegrityError):
            self.engine.correct_reading(old_id, bad)
        self.assertEqual(self.engine.get_reading(old_id)["enable"], 1)

    def test_disabled_reading_leaves_the_period(self):
        reading_id = self.add("2026-10-01 08:00:00", 120, 80)
        self.engine.disable_reading(reading_id)
        self.assertEqual(self.engine.get_readings(*OCTOBER), [])
        self.assertEqual(self.engine.get_reading_count(), 0)

    def test_second_is_taken(self):
        self.add("2026-10-01 08:00:00", 120, 80)
        self.assertTrue(self.engine.is_taken("2026-10-01 08:00:00"))
        self.assertFalse(self.engine.is_taken("2026-10-01 08:00:01"))

    def test_second_of_the_corrected_reading_is_free(self):
        reading_id = self.add("2026-10-01 08:00:00", 120, 80)
        self.assertFalse(self.engine.is_taken("2026-10-01 08:00:00",
                                              reading_id))

    def test_settings_change_together(self):
        self.engine.set_settings({"systolic_threshold_mmhg": "130",
                                  "diastolic_threshold_mmhg": "80"})
        self.assertEqual(self.engine.get_threshold().get_caption(),
                         "130/80 mmHg")

    def test_unknown_setting_changes_nothing(self):
        with self.assertRaises(ValueError):
            self.engine.set_settings({"systolic_threshold_mmhg": "130",
                                      "colour": "red"})
        self.assertEqual(self.engine.get_setting("systolic_threshold_mmhg"),
                         "135")

    def test_bounds_of_a_period(self):
        self.assertEqual(self.engine.get_bounds(*OCTOBER),
                         ("2026-10-01 00:00:00", "2026-10-31 23:59:59"))

    def test_day_is_shown_day_first(self):
        self.assertEqual(
            self.engine.get_shown_day(datetime.date(2026, 3, 7)),
            "07/03/2026")


if __name__ == "__main__":
    unittest.main()
