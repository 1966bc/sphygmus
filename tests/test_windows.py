# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the main window and its parts, opened for real.

The application on a diary in memory. They need a display and skip
themselves without one; run under xvfb-run, or a pass says nothing.

No test here presses what opens a message box: a box waits for a person,
and the suite would wait with it. What a box would say is asked of the
method that decides it.
"""

import datetime
import os
import unittest

from log import Log

HAS_DISPLAY = bool(os.environ.get("DISPLAY"))

if HAS_DISPLAY:
    from ui.app import App

SEATED = 1
LYING = 2


@unittest.skipUnless(HAS_DISPLAY, "no display")
class WindowTestCase(unittest.TestCase):

    def setUp(self):
        self.app = App(database=":memory:", log=Log(os.devnull),
                       theme="clam")
        self.app.update()
        self.engine = self.app.engine
        self.main = self.app.main
        self.entry = self.main.entry

    def tearDown(self):
        if self.app.winfo_exists():
            self.app.destroy()

    def add(self, moment, systolic, diastolic, rate=70, position=SEATED):
        values = self.engine.get_reading_values(
            self.engine.get_stored(moment), position, systolic, diastolic,
            rate)
        reading_id = self.engine.add_reading(values)
        self.engine.events.notify("readings", reading_id)
        return reading_id

    def get_today_at(self, hour, minute):
        return datetime.datetime.combine(datetime.date.today(),
                                         datetime.time(hour, minute))

    def type_reading(self, systolic, diastolic, rate, time=None):
        self.entry.systolic.set(systolic)
        self.entry.diastolic.set(diastolic)
        self.entry.heart_rate.set(rate)
        if time is not None:
            self.entry.time.set(time)


class AppTestCase(WindowTestCase):

    def test_class_name_is_one_lowercase_word(self):
        self.assertEqual(self.app.winfo_class(), "Sphygmus")
        self.assertEqual(self.app.tk.call("tk", "appname"), "sphygmus")

    def test_opens_centred_across_the_screen(self):
        middle = self.app.winfo_rootx() + self.app.winfo_width() / 2
        self.assertAlmostEqual(middle, self.app.winfo_screenwidth() / 2,
                               delta=2)

    def test_opens_with_the_keyboard_on_systolic(self):
        self.assertIs(self.app.focus_get(), self.entry.ent_systolic)

    def test_icon_comes_in_every_size(self):
        sizes = [icon.width() for icon in self.app.icons]
        self.assertEqual(sizes, [16, 32, 48, 64, 128])

    def test_title_is_the_name(self):
        self.assertEqual(self.app.title(), "Sphygmus")

    def test_status_bar_counts_the_readings(self):
        self.assertTrue(self.main.status.get().startswith(
            "0 readings in the diary"))

    def test_status_bar_follows_a_new_reading(self):
        self.add(self.get_today_at(0, 1), 128, 79)
        self.assertTrue(self.main.status.get().startswith(
            "1 readings in the diary"))

    def test_closed_main_stops_listening(self):
        self.main.destroy()
        self.assertEqual(self.engine.events.subscribers["readings"], [])
        self.assertEqual(self.engine.events.subscribers["settings"], [])

    def test_unknown_theme_is_refused(self):
        with self.assertRaises(ValueError):
            App(database=":memory:", log=Log(os.devnull), theme="nothing")


class EntryTestCase(WindowTestCase):

    def test_time_follows_the_clock_untouched(self):
        self.entry.time.set("00:00:00")
        self.entry.shown_time = "00:00:00"
        self.entry.on_tick()
        self.assertNotEqual(self.entry.time.get(), "00:00:00")

    def test_time_touched_is_left_alone(self):
        self.entry.time.set("07:30:00")
        self.entry.on_tick()
        self.assertEqual(self.entry.time.get(), "07:30:00")

    def test_empty_number_is_a_problem(self):
        self.type_reading("128", "", "66")
        self.assertIn("all three", self.entry.get_problem())

    def test_minus_alone_is_a_problem_not_a_crash(self):
        self.type_reading("-", "79", "66")
        self.assertIn("all three", self.entry.get_problem())

    def test_systolic_not_above_diastolic_is_a_problem(self):
        self.type_reading("79", "128", "66")
        self.assertIn("higher", self.entry.get_problem())

    def test_bad_time_is_a_problem(self):
        self.type_reading("128", "79", "66", "25:00")
        self.assertIn("not a date and a time", self.entry.get_problem())

    def test_time_without_seconds_is_read(self):
        self.type_reading("128", "79", "66", "07:30")
        self.assertEqual(self.entry.get_time(), datetime.time(7, 30))

    def test_future_is_a_problem(self):
        self.type_reading("128", "79", "66")
        self.entry.date.set_date(datetime.date.today()
                                 + datetime.timedelta(days=1))
        self.assertIn("not come yet", self.entry.get_problem())

    def test_taken_second_is_a_problem(self):
        self.add(self.get_today_at(0, 1), 128, 79)
        self.type_reading("130", "80", "66", "00:01:00")
        self.assertIn("already a reading", self.entry.get_problem())

    def test_save_stores_and_clears(self):
        self.type_reading("128", "79", "66", "00:02:00")
        self.entry.on_save()
        self.assertEqual(self.engine.get_reading_count(), 1)
        self.assertEqual(self.entry.systolic.get(), "")
        self.assertTrue(self.entry.message.get().startswith("Saved"))

    def test_save_reaches_the_list(self):
        self.type_reading("128", "79", "66", "00:02:00")
        self.entry.on_save()
        self.assertEqual(len(self.main.readings.tree.get_children()), 1)

    def test_correction_keeps_the_second_and_replaces(self):
        old_id = self.add(self.get_today_at(0, 3), 210, 79)
        self.entry.set_correction(old_id)
        self.assertEqual(self.entry.time.get(), "00:03:00")
        self.entry.systolic.set("120")
        self.entry.on_save()
        self.assertEqual(self.engine.get_reading(old_id)["enable"], 0)
        self.assertEqual(self.engine.get_reading_count(), 1)
        self.assertTrue(self.entry.message.get().startswith("Corrected"))

    def test_escape_gives_up_the_correction(self):
        old_id = self.add(self.get_today_at(0, 3), 210, 79)
        self.entry.set_correction(old_id)
        self.entry.on_cancel()
        self.assertIsNone(self.entry.correcting)
        self.assertEqual(self.entry.systolic.get(), "")
        self.assertEqual(self.engine.get_reading(old_id)["enable"], 1)


class ListTestCase(WindowTestCase):

    def test_reading_over_the_threshold_is_marked(self):
        over_id = self.add(self.get_today_at(0, 1), 135, 70)
        under_id = self.add(self.get_today_at(0, 2), 134, 84)
        tree = self.main.readings.tree
        self.assertEqual(tree.item(str(over_id), "tags"), ("over",))
        self.assertEqual(tree.item(str(under_id), "tags"), "")

    def test_new_threshold_redraws_the_marks(self):
        reading_id = self.add(self.get_today_at(0, 1), 132, 70)
        self.engine.set_settings({"systolic_threshold_mmhg": "130",
                                  "diastolic_threshold_mmhg": "80"})
        self.engine.events.notify("settings", None)
        tree = self.main.readings.tree
        self.assertEqual(tree.item(str(reading_id), "tags"), ("over",))

    def test_date_is_shown_day_first(self):
        reading_id = self.add(self.get_today_at(0, 1), 128, 79)
        values = self.main.readings.tree.item(str(reading_id), "values")
        self.assertEqual(values[0],
                         datetime.date.today().strftime("%d/%m/%Y"))

    def test_double_click_fills_the_strip(self):
        reading_id = self.add(self.get_today_at(0, 1), 128, 79)
        self.main.readings.tree.focus(str(reading_id))
        self.main.readings.on_double_click()
        self.assertEqual(self.entry.correcting, reading_id)
        self.assertEqual(self.entry.systolic.get(), "128")

    def test_disabled_reading_leaves_the_list(self):
        reading_id = self.add(self.get_today_at(0, 1), 128, 79)
        self.engine.disable_reading(reading_id)
        self.engine.events.notify("readings", None)
        self.assertEqual(self.main.readings.tree.get_children(), ())

    def test_period_excludes_older_readings(self):
        old = datetime.datetime.now() - datetime.timedelta(days=60)
        self.add(old.replace(microsecond=0), 128, 79)
        self.assertEqual(self.main.readings.tree.get_children(), ())

    def test_impossible_period_shows_nothing(self):
        self.add(self.get_today_at(0, 1), 128, 79)
        self.main.start.set_date(datetime.date.today()
                                 + datetime.timedelta(days=1))
        self.main.on_period()
        self.assertEqual(self.main.readings.tree.get_children(), ())
        self.assertIn("no period", self.main.status.get())


class StatisticsTestCase(WindowTestCase):

    def test_one_row_per_position(self):
        self.add(self.get_today_at(0, 1), 120, 80, 60)
        self.add(self.get_today_at(0, 2), 131, 81, 71)
        self.add(self.get_today_at(0, 3), 110, 70, 58, LYING)
        tree = self.main.statistics.tree
        seated = tree.item(str(SEATED), "values")
        self.assertEqual(seated[0], "seated")
        self.assertEqual(seated[1], "2")
        # 125.5 rounds up, as a person rounds.
        self.assertEqual(seated[2], "126 (120-131)")
        self.assertTrue(tree.exists(str(LYING)))


if __name__ == "__main__":
    unittest.main()
