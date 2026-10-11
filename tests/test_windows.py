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
from tkinter import ttk

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

    def test_database_menu_holds_the_diary_as_a_file(self):
        self.assertEqual(self.get_labels(self.main.mnu_database),
                         ["Back up", "Restore a backup...", "Check",
                          "Vacuum", "Start a new diary..."])

    def test_file_menu_is_the_only_menu_but_help(self):
        menu = self.main.mnu_file
        labels = [menu.entrycget(index, "label")
                  for index in range(menu.index("end") + 1)
                  if menu.type(index) != "separator"]
        self.assertEqual(labels, ["Database", "Demo diary", "Report...",
                                  "Settings...", "Exit"])

    def test_buttons_have_one_letter_each_and_close_is_c(self):
        letters = {}
        for widget in self.engine.tools.get_widgets(self.main):
            if isinstance(widget, ttk.Button):
                index = int(str(widget.cget("underline")))
                letters[widget.cget("text")] = widget.cget("text")[index]
        self.assertEqual(letters, {"New": "N", "Edit": "E", "Delete": "D",
                                   "Plot": "P", "Close": "C"})

    def test_how_to_measure_shows_the_text_and_its_source(self):
        self.main.on_guide()
        self.app.update()
        guide = self.engine.windows.get("guide")
        text = guide.text.get("1.0", "end")
        self.assertTrue(text.startswith("HOW TO MEASURE"))
        self.assertIn("PMC9904446", text)
        self.assertEqual(str(guide.text.cget("state")), "disabled")

    def test_report_is_written_and_opened(self):
        opened = []
        self.main.set_opened = opened.append
        self.add(self.get_today_at(0, 1), 128, 79)
        self.main.on_report()
        self.assertEqual(len(opened), 1)
        self.assertTrue(opened[0].endswith(".pdf"))
        self.assertTrue(os.path.getsize(opened[0]) > 0)
        os.remove(opened[0])

    def test_check_says_sound_on_the_status_bar(self):
        self.main.on_check()
        self.assertIn("sound", self.main.status.get())

    def test_demo_opens_invented_readings_and_says_so(self):
        self.main.demo.set(True)
        self.main.on_demo()
        self.assertTrue(self.engine.is_demo())
        self.assertEqual(self.app.title(), "Sphygmus - DEMO")
        self.assertGreater(len(self.tree.get_children()), 0)
        self.assertIn("Demo diary", self.main.status.get())

    def test_leaving_the_demo_brings_the_diary_back(self):
        # A file: a diary in memory does not survive being closed.
        folder = tempfile.mkdtemp()
        app = App(database=os.path.join(folder, "diary.sl3"),
                  log=Log(os.devnull), theme="clam")
        try:
            values = app.engine.get_reading_values(
                app.engine.get_stored(self.get_today_at(0, 1)), SEATED, 128,
                79, 66)
            app.engine.add_reading(values)
            app.main.demo.set(True)
            app.main.on_demo()
            demo = app.engine.demo_folder
            app.main.demo.set(False)
            app.main.on_demo()
            self.assertFalse(app.engine.is_demo())
            self.assertEqual(app.title(), "Sphygmus")
            self.assertEqual(
                len(app.main.readings.tree.get_children()), 1)
            self.assertFalse(os.path.exists(demo))
        finally:
            app.destroy()
            shutil.rmtree(folder)

    def test_closing_in_the_demo_removes_it(self):
        folder = tempfile.mkdtemp()
        app = App(database=os.path.join(folder, "diary.sl3"),
                  log=Log(os.devnull), theme="clam")
        try:
            app.main.demo.set(True)
            app.main.on_demo()
            demo = app.engine.demo_folder
            app.set_closed()
            self.assertFalse(os.path.exists(demo))
        finally:
            shutil.rmtree(folder)

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
        form.set_clock()
        self.assertNotEqual(form.time.get(), "00:00:00")

    def test_time_touched_is_left_alone(self):
        form = self.open_new()
        form.time.set("07:30:00")
        form.set_clock()
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


class SettingsTestCase(WindowTestCase):

    def open_settings(self):
        self.main.on_settings_window()
        self.app.update()
        return self.engine.windows.get("settings")

    def test_settings_open_with_the_diary_values(self):
        window = self.open_settings()
        self.assertEqual(window.systolic.get(), "135")
        self.assertEqual(window.diastolic.get(), "85")
        self.assertEqual(window.period_days.get(), "30")

    def test_opening_twice_keeps_one_window(self):
        first = self.open_settings()
        second = self.open_settings()
        self.assertIs(first, second)

    def test_threshold_not_a_number_is_a_problem(self):
        window = self.open_settings()
        window.systolic.set("")
        self.assertIn("thresholds", window.get_problem())

    def test_systolic_threshold_below_diastolic_is_a_problem(self):
        window = self.open_settings()
        window.systolic.set("80")
        self.assertIn("thresholds", window.get_problem())

    def test_zero_days_is_a_problem(self):
        window = self.open_settings()
        window.period_days.set("0")
        self.assertIn("from 1", window.get_problem())

    def test_save_redraws_the_marks(self):
        reading_id = self.add(self.get_today_at(0, 1), 132, 70)
        window = self.open_settings()
        window.systolic.set("130")
        window.diastolic.set("80")
        window.on_save()
        self.app.update()
        self.assertIsNone(self.engine.windows.get("settings"))
        self.assertEqual(self.tree.item(str(reading_id), "tags"), ("over",))

    def test_new_days_move_the_period(self):
        window = self.open_settings()
        window.period_days.set("7")
        window.on_save()
        self.assertEqual(self.main.start.get_date(),
                         datetime.date.today() - datetime.timedelta(days=7))

    def test_new_threshold_leaves_a_period_chosen_by_hand(self):
        chosen = datetime.date.today() - datetime.timedelta(days=3)
        self.main.start.set_date(chosen)
        window = self.open_settings()
        window.systolic.set("130")
        window.on_save()
        self.assertEqual(self.main.start.get_date(), chosen)

    def test_name_is_saved_without_extra_spaces(self):
        window = self.open_settings()
        window.patient_name.set("  sample   name ")
        window.on_save()
        self.assertEqual(self.engine.get_setting("patient_name"),
                         "sample name")


class ChartTestCase(WindowTestCase):

    def open_chart(self):
        self.main.on_chart()
        self.app.update()
        return self.engine.windows.get("chart")

    def test_empty_period_says_so(self):
        chart = self.open_chart()
        self.assertEqual(len(chart.canvas.find_withtag("empty")), 1)

    def test_one_dot_each_value_and_two_threshold_lines(self):
        self.add(self.get_today_at(0, 1), 128, 79)
        self.add(self.get_today_at(0, 2), 140, 90, position=LYING)
        canvas = self.open_chart().canvas
        self.assertEqual(len(canvas.find_withtag("systolic")), 2)
        self.assertEqual(len(canvas.find_withtag("diastolic")), 2)
        self.assertEqual(len(canvas.find_withtag("threshold")), 2)

    def test_lying_dot_is_hollow(self):
        self.add(self.get_today_at(0, 2), 140, 90, position=LYING)
        canvas = self.open_chart().canvas
        dot = canvas.find_withtag("systolic")[0]
        self.assertEqual(canvas.itemcget(dot, "fill"), "#ffffff")

    def test_higher_value_is_drawn_higher(self):
        self.add(self.get_today_at(0, 1), 128, 79)
        canvas = self.open_chart().canvas
        systolic = canvas.coords(canvas.find_withtag("systolic")[0])
        diastolic = canvas.coords(canvas.find_withtag("diastolic")[0])
        self.assertLess(systolic[1], diastolic[1])

    def test_new_reading_is_drawn(self):
        canvas = self.open_chart().canvas
        self.add(self.get_today_at(0, 1), 128, 79)
        self.assertEqual(len(canvas.find_withtag("systolic")), 1)

    def test_chart_follows_the_period(self):
        self.add(self.get_today_at(0, 1), 128, 79)
        canvas = self.open_chart().canvas
        self.main.start.set_date(datetime.date.today()
                                 + datetime.timedelta(days=1))
        self.main.on_period()
        self.assertEqual(len(canvas.find_withtag("empty")), 1)

    def test_opening_twice_keeps_one_chart(self):
        self.assertIs(self.open_chart(), self.open_chart())

    def test_closed_chart_stops_listening(self):
        self.open_chart().on_cancel()
        self.app.update()
        self.assertEqual(len(self.engine.events.subscribers["readings"]), 3)


class ListTestCase(WindowTestCase):

    def show(self, shown):
        self.main.readings.shown.set(shown)
        self.main.readings.on_shown()

    def test_removed_reading_is_grey_under_removed(self):
        reading_id = self.add(self.get_today_at(0, 1), 140, 79)
        self.engine.disable_reading(reading_id)
        self.show("removed")
        self.assertEqual(self.tree.item(str(reading_id), "tags"),
                         ("discarded",))

    def test_all_shows_both_and_counts_only_the_active(self):
        kept = self.add(self.get_today_at(0, 1), 128, 79)
        gone = self.add(self.get_today_at(0, 2), 129, 79)
        self.engine.disable_reading(gone)
        self.show("all")
        self.assertEqual(set(self.tree.get_children()),
                         {str(kept), str(gone)})
        self.assertTrue(self.main.readings.count.get().startswith(
            "1 readings"))
        self.assertIn("1 removed", self.main.readings.count.get())

    def test_active_hides_the_removed(self):
        gone = self.add(self.get_today_at(0, 2), 129, 79)
        self.engine.disable_reading(gone)
        self.show("active")
        self.assertEqual(self.tree.get_children(), ())

    def test_removed_reading_opens_unticked(self):
        gone = self.add(self.get_today_at(0, 2), 129, 79)
        self.engine.disable_reading(gone)
        self.show("removed")
        self.main.on_edit(gone)
        form = self.get_form()
        self.assertFalse(form.enable.get())
        self.assertTrue(form.title().endswith("- removed"))

    def test_ticking_brings_a_removed_reading_back(self):
        gone = self.add(self.get_today_at(0, 2), 129, 79)
        self.engine.disable_reading(gone)
        self.main.on_edit(gone)
        form = self.get_form()
        form.enable.set(True)
        form.on_save()
        self.app.update()
        self.assertEqual(self.engine.get_reading(gone)["enable"], 1)
        self.assertEqual(self.tree.focus(), str(gone))

    def test_unticking_takes_a_reading_out(self):
        reading_id = self.add(self.get_today_at(0, 2), 129, 79)
        self.main.on_edit(reading_id)
        form = self.get_form()
        form.enable.set(False)
        form.on_save()
        self.assertEqual(self.engine.get_reading(reading_id)["enable"], 0)

    def test_corrected_reading_cannot_be_ticked_back(self):
        old_id = self.add(self.get_today_at(0, 3), 210, 79)
        self.main.on_edit(old_id)
        form = self.get_form()
        form.systolic.set("120")
        form.on_save()
        self.main.on_edit(old_id)
        form = self.get_form()
        form.enable.set(True)
        self.assertIn("already a reading", form.get_problem())

    def test_new_reading_cannot_be_unticked(self):
        form = self.open_new()
        self.assertTrue(form.chk_enable.instate(("disabled",)))

    def test_removed_reading_can_come_back(self):
        gone = self.add(self.get_today_at(0, 2), 129, 79)
        self.engine.disable_reading(gone)
        self.assertTrue(self.engine.can_enable(gone))
        self.engine.enable_reading(gone)
        self.assertEqual(self.engine.get_reading_count(), 1)

    def test_corrected_reading_cannot_come_back(self):
        old_id = self.add(self.get_today_at(0, 3), 210, 79)
        values = self.engine.get_reading_values(
            self.engine.get_stored(self.get_today_at(0, 3)), SEATED, 120, 79,
            70)
        self.engine.correct_reading(old_id, values)
        self.assertFalse(self.engine.can_enable(old_id))

    def test_delete_without_a_selection_says_so(self):
        self.main.on_delete()
        self.assertIn("Select a reading", self.main.status.get())


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
