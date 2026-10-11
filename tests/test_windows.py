# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the main window, the list and the form, opened for real.

The application on a diary in memory. They need a display and skip
themselves without one; run under xvfb-run, or a pass says nothing.

No test here presses what opens a message box: a box waits for a person,
and the suite would wait with it. What a box would say is asked of the
method that decides it.
"""

import datetime
import os
import shutil
import tempfile
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
        self.tree = self.main.readings.tree

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

    def get_form(self):
        return self.engine.windows.get("reading")

    def open_new(self):
        self.main.on_new()
        self.app.update()
        return self.get_form()

    def type_reading(self, form, systolic, diastolic, rate, time=None):
        form.systolic.set(systolic)
        form.diastolic.set(diastolic)
        form.heart_rate.set(rate)
        if time is not None:
            form.time.set(time)


class AppTestCase(WindowTestCase):

    def test_class_name_is_one_lowercase_word(self):
        self.assertEqual(self.app.winfo_class(), "Sphygmus")
        self.assertEqual(self.app.tk.call("tk", "appname"), "sphygmus")

    def test_opens_centred_across_the_screen(self):
        middle = self.app.winfo_rootx() + self.app.winfo_width() / 2
        self.assertAlmostEqual(middle, self.app.winfo_screenwidth() / 2,
                               delta=2)

    def test_opens_with_the_keyboard_on_the_list(self):
        self.assertIs(self.app.focus_get(), self.tree)

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

    def test_fresh_diary_empties_the_window(self):
        folder = tempfile.mkdtemp()
        app = App(database=os.path.join(folder, "diary.sl3"),
                  log=Log(os.devnull), theme="clam")
        try:
            values = app.engine.get_reading_values(
                app.engine.get_stored(self.get_today_at(0, 1)), SEATED, 128,
                79, 66)
            app.engine.add_reading(values)
            app.engine.events.notify("readings", None)
            app.main.on_new()
            app.main.set_fresh_diary()
            app.update()
            self.assertEqual(app.main.readings.tree.get_children(), ())
            self.assertIsNone(app.engine.windows.get("reading"))
            self.assertIn("The old one is", app.main.status.get())
        finally:
            app.destroy()
            shutil.rmtree(folder)

    def get_labels(self, menu):
        labels = []
        for index in range(menu.index("end") + 1):
            if menu.type(index) == "command":
                labels.append(menu.entrycget(index, "label"))
        return labels

    def test_file_menu_holds_the_diary_as_a_file(self):
        self.assertEqual(self.get_labels(self.main.mnu_file),
                         ["Back up the diary", "Restore a backup...",
                          "Check the diary", "Vacuum the diary",
                          "Start a new diary...", "Exit"])

    def test_check_says_sound_on_the_status_bar(self):
        self.main.on_check()
        self.assertIn("sound", self.main.status.get())

    def test_unknown_theme_is_refused(self):
        with self.assertRaises(ValueError):
            App(database=":memory:", log=Log(os.devnull), theme="nothing")


class FormTestCase(WindowTestCase):

    def test_new_opens_a_form_on_systolic(self):
        form = self.open_new()
        self.assertEqual(form.title(), "New reading")
        self.assertIs(self.app.focus_get(), form.ent_systolic)

    def test_new_starts_in_the_last_position(self):
        self.add(self.get_today_at(0, 1), 128, 79, position=LYING)
        form = self.open_new()
        self.assertEqual(form.position_id.get(), LYING)

    def test_time_follows_the_clock_untouched(self):
        form = self.open_new()
        form.time.set("00:00:00")
        form.shown_time = "00:00:00"
        form.on_tick()
        self.assertNotEqual(form.time.get(), "00:00:00")

    def test_time_touched_is_left_alone(self):
        form = self.open_new()
        form.time.set("07:30:00")
        form.on_tick()
        self.assertEqual(form.time.get(), "07:30:00")

    def test_empty_number_is_a_problem(self):
        form = self.open_new()
        self.type_reading(form, "128", "", "66")
        self.assertIn("all three", form.get_problem())

    def test_minus_alone_is_a_problem_not_a_crash(self):
        form = self.open_new()
        self.type_reading(form, "-", "79", "66")
        self.assertIn("all three", form.get_problem())

    def test_systolic_not_above_diastolic_is_a_problem(self):
        form = self.open_new()
        self.type_reading(form, "79", "128", "66")
        self.assertIn("higher", form.get_problem())

    def test_bad_time_is_a_problem(self):
        form = self.open_new()
        self.type_reading(form, "128", "79", "66", "25:00")
        self.assertIn("not a date and a time", form.get_problem())

    def test_time_without_seconds_is_read(self):
        form = self.open_new()
        self.type_reading(form, "128", "79", "66", "07:30")
        self.assertEqual(form.get_time(), datetime.time(7, 30))

    def test_future_is_a_problem(self):
        form = self.open_new()
        self.type_reading(form, "128", "79", "66")
        form.date.set_date(datetime.date.today()
                           + datetime.timedelta(days=1))
        self.assertIn("not come yet", form.get_problem())

    def test_taken_second_is_a_problem(self):
        self.add(self.get_today_at(0, 1), 128, 79)
        form = self.open_new()
        self.type_reading(form, "130", "80", "66", "00:01:00")
        self.assertIn("already a reading", form.get_problem())

    def test_save_closes_and_lands_on_the_new_row(self):
        self.add(self.get_today_at(0, 1), 120, 79)
        form = self.open_new()
        self.type_reading(form, "128", "79", "66", "00:02:00")
        form.on_save()
        self.app.update()
        self.assertIsNone(self.get_form())
        self.assertEqual(self.engine.get_reading_count(), 2)
        saved = self.engine.get_readings(datetime.date.today(),
                                         datetime.date.today())[0]
        self.assertEqual(self.tree.focus(), str(saved["reading_id"]))

    def test_edit_opens_the_selected_reading(self):
        reading_id = self.add(self.get_today_at(0, 3), 128, 79)
        self.engine.tools.set_selected(self.tree, str(reading_id))
        self.main.on_edit()
        self.app.update()
        form = self.get_form()
        self.assertEqual(form.reading_id, reading_id)
        self.assertEqual(form.systolic.get(), "128")
        self.assertEqual(form.time.get(), "00:03:00")

    def test_edit_without_a_selection_says_so(self):
        self.main.on_edit()
        self.assertIsNone(self.get_form())
        self.assertIn("Select a reading", self.main.status.get())

    def test_double_click_on_another_row_moves_the_form(self):
        first = self.add(self.get_today_at(0, 3), 128, 79)
        second = self.add(self.get_today_at(0, 4), 131, 82)
        for reading_id in (first, second):
            self.tree.focus(str(reading_id))
            self.main.readings.on_double_click()
            self.app.update()
        forms = [child for child in self.app.winfo_children()
                 if child.winfo_name() == "reading"]
        self.assertEqual(len(forms), 1)
        self.assertEqual(self.get_form().reading_id, second)

    def test_correction_replaces_and_lands_on_the_new_row(self):
        old_id = self.add(self.get_today_at(0, 3), 210, 79)
        self.main.on_edit(old_id)
        form = self.get_form()
        form.systolic.set("120")
        form.on_save()
        self.app.update()
        self.assertEqual(self.engine.get_reading(old_id)["enable"], 0)
        self.assertEqual(self.engine.get_reading_count(), 1)
        self.assertNotEqual(self.tree.focus(), str(old_id))
        new_id = int(self.tree.focus())
        self.assertEqual(self.engine.get_reading(new_id)["systolic_mmhg"],
                         120)

    def test_unchanged_correction_writes_nothing(self):
        reading_id = self.add(self.get_today_at(0, 3), 128, 79)
        self.main.on_edit(reading_id)
        self.get_form().on_save()
        self.app.update()
        self.assertEqual(self.engine.get_reading(reading_id)["enable"], 1)
        self.assertEqual(self.tree.focus(), str(reading_id))

    def test_close_writes_nothing(self):
        form = self.open_new()
        self.type_reading(form, "128", "79", "66", "00:02:00")
        form.on_cancel()
        self.app.update()
        self.assertIsNone(self.get_form())
        self.assertEqual(self.engine.get_reading_count(), 0)


class ListTestCase(WindowTestCase):

    def test_reading_over_the_threshold_is_marked(self):
        over_id = self.add(self.get_today_at(0, 1), 135, 70)
        under_id = self.add(self.get_today_at(0, 2), 134, 84)
        self.assertEqual(self.tree.item(str(over_id), "tags"), ("over",))
        self.assertEqual(self.tree.item(str(under_id), "tags"), "")

    def test_new_threshold_redraws_the_marks(self):
        reading_id = self.add(self.get_today_at(0, 1), 132, 70)
        self.engine.set_settings({"systolic_threshold_mmhg": "130",
                                  "diastolic_threshold_mmhg": "80"})
        self.engine.events.notify("settings", None)
        self.assertEqual(self.tree.item(str(reading_id), "tags"), ("over",))

    def test_date_is_shown_day_first(self):
        reading_id = self.add(self.get_today_at(0, 1), 128, 79)
        values = self.tree.item(str(reading_id), "values")
        self.assertEqual(values[0],
                         datetime.date.today().strftime("%d/%m/%Y"))

    def test_disabled_reading_leaves_the_list(self):
        reading_id = self.add(self.get_today_at(0, 1), 128, 79)
        self.engine.disable_reading(reading_id)
        self.engine.events.notify("readings", None)
        self.assertEqual(self.tree.get_children(), ())

    def test_period_excludes_older_readings(self):
        old = datetime.datetime.now() - datetime.timedelta(days=60)
        self.add(old.replace(microsecond=0), 128, 79)
        self.assertEqual(self.tree.get_children(), ())

    def test_impossible_period_shows_nothing(self):
        self.add(self.get_today_at(0, 1), 128, 79)
        self.main.start.set_date(datetime.date.today()
                                 + datetime.timedelta(days=1))
        self.main.on_period()
        self.assertEqual(self.tree.get_children(), ())
        self.assertIn("no period", self.main.status.get())


class StatisticsTestCase(WindowTestCase):

    def test_one_line_per_position(self):
        self.add(self.get_today_at(0, 1), 120, 80, 60)
        self.add(self.get_today_at(0, 2), 131, 81, 71)
        self.add(self.get_today_at(0, 3), 110, 70, 58, LYING)
        seated, lying = self.main.statistics.lines
        # 125.5 rounds up, as a person rounds.
        self.assertEqual(seated, ("seated", "2", "126 (120-131)",
                                  "81 (80-81)", "66 (60-71)"))
        self.assertEqual(lying[0], "lying")

    def test_no_readings_no_lines(self):
        self.assertEqual(self.main.statistics.lines, [])


if __name__ == "__main__":
    unittest.main()
