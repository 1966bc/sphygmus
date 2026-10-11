# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the domain: threshold, scale and timeline."""

import datetime
import unittest

from pressure.scale import Scale
from pressure.threshold import Threshold
from pressure.timeline import Timeline


class ThresholdTestCase(unittest.TestCase):

    def setUp(self):
        self.threshold = Threshold("135", "85")

    def test_below_both_is_not_over(self):
        self.assertFalse(self.threshold.is_over(134, 84))

    def test_systolic_at_the_limit_is_over(self):
        self.assertTrue(self.threshold.is_over(135, 70))

    def test_diastolic_at_the_limit_is_over(self):
        self.assertTrue(self.threshold.is_over(120, 85))

    def test_caption(self):
        self.assertEqual(self.threshold.get_caption(), "135/85 mmHg")

    def test_text_that_is_not_a_number_is_refused(self):
        with self.assertRaises(ValueError):
            Threshold("13S", "85")

    def test_empty_limit_is_refused(self):
        with self.assertRaises(ValueError):
            Threshold("", "85")

    def test_zero_is_refused(self):
        with self.assertRaises(ValueError):
            Threshold("0", "85")

    def test_systolic_not_above_diastolic_is_refused(self):
        with self.assertRaises(ValueError):
            Threshold("85", "135")


class ScaleTestCase(unittest.TestCase):

    def test_bounds_are_round_and_contain_the_values(self):
        scale = Scale(62, 151)
        self.assertEqual((scale.lower, scale.upper, scale.step),
                         (60, 160, 20))

    def test_ticks_run_from_lower_to_upper(self):
        scale = Scale(62, 151)
        self.assertEqual(scale.get_ticks(), [60, 80, 100, 120, 140, 160])

    def test_fraction(self):
        scale = Scale(60, 160)
        self.assertEqual(scale.calc_fraction(110), 0.5)

    def test_one_value_still_has_a_height(self):
        scale = Scale(120, 120)
        self.assertLess(scale.lower, scale.upper)

    def test_low_above_high_is_refused(self):
        with self.assertRaises(ValueError):
            Scale(150, 60)


class TimelineTestCase(unittest.TestCase):

    def setUp(self):
        self.timeline = Timeline(datetime.date(2026, 10, 1),
                                 datetime.date(2026, 10, 10))

    def test_days_are_counted_inclusive(self):
        self.assertEqual(self.timeline.get_days(), 10)

    def test_first_instant_is_zero(self):
        moment = datetime.datetime(2026, 10, 1, 0, 0, 0)
        self.assertEqual(self.timeline.calc_fraction(moment), 0.0)

    def test_start_of_the_sixth_day_is_half_way(self):
        moment = datetime.datetime(2026, 10, 6, 0, 0, 0)
        self.assertEqual(self.timeline.calc_fraction(moment), 0.5)

    def test_last_minute_is_still_inside(self):
        moment = datetime.datetime(2026, 10, 10, 23, 59, 0)
        self.assertLess(self.timeline.calc_fraction(moment), 1.0)

    def test_ticks_never_exceed_the_asked_number(self):
        timeline = Timeline(datetime.date(2026, 1, 1),
                            datetime.date(2026, 12, 31))
        self.assertLessEqual(len(timeline.get_ticks(8)), 8)

    def test_short_period_has_a_tick_a_day(self):
        self.assertEqual(len(self.timeline.get_ticks(10)), 10)

    def test_period_backwards_is_refused(self):
        with self.assertRaises(ValueError):
            Timeline(datetime.date(2026, 10, 10), datetime.date(2026, 10, 1))


if __name__ == "__main__":
    unittest.main()
