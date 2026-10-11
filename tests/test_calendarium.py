# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the date widget, on a real Tk.

They need a display and skip themselves where there is none. A skipped test
passes, so run them on a screen of their own:

    xvfb-run -a python3 -m unittest discover -s tests -v
"""

import datetime
import os
import tkinter as tk
import unittest

from ui.calendarium import DATE_CHANGED, Calendarium

HAS_DISPLAY = bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(HAS_DISPLAY, "no display")
class CalendariumTestCase(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.calendarium = Calendarium(self.root, "From")
        self.calendarium.pack()
        self.root.update()
        self.events = []
        self.calendarium.bind(DATE_CHANGED, self.on_changed)

    def tearDown(self):
        self.root.destroy()

    def on_changed(self, evt=None):
        self.events.append(evt)

    def test_starts_on_today(self):
        self.assertEqual(self.calendarium.get_date(), datetime.date.today())

    def test_date_set_is_read_back(self):
        self.calendarium.set_date(datetime.date(2026, 10, 11))
        self.assertEqual(self.calendarium.get_date(),
                         datetime.date(2026, 10, 11))

    def test_iso_is_the_stored_form(self):
        self.calendarium.set_date(datetime.date(2026, 3, 7))
        self.assertEqual(self.calendarium.get_iso(), "2026-03-07")

    def test_impossible_date_is_none(self):
        self.calendarium.day.set("31")
        self.calendarium.month.set("2")
        self.assertIsNone(self.calendarium.get_date())
        self.assertIsNone(self.calendarium.get_iso())
        self.assertFalse(self.calendarium.is_valid())

    def test_empty_field_is_none(self):
        self.calendarium.day.set("")
        self.assertIsNone(self.calendarium.get_date())

    def test_month_thirteen_is_none(self):
        self.calendarium.month.set("13")
        self.assertIsNone(self.calendarium.get_date())

    def test_letter_is_refused_at_the_keystroke(self):
        spin = self.calendarium.spins["day"]
        spin.delete(0, tk.END)
        spin.insert(0, "1a")
        self.assertEqual(self.calendarium.day.get(), "")

    def test_superscript_digit_is_refused(self):
        spin = self.calendarium.spins["day"]
        spin.delete(0, tk.END)
        spin.insert(0, "²")
        self.assertEqual(self.calendarium.day.get(), "")

    def test_set_date_announces_once(self):
        self.calendarium.set_date(datetime.date(2026, 1, 2))
        self.root.update()
        self.assertEqual(len(self.events), 1)

    def test_destroy_with_an_event_pending_raises_nothing(self):
        self.calendarium.set_date(datetime.date(2026, 1, 2))
        self.calendarium.destroy()
        self.root.update()
        self.assertEqual(self.events, [])

    def test_disabled_fields_say_so(self):
        self.calendarium.set_state(tk.DISABLED)
        for spin in self.calendarium.spins.values():
            self.assertEqual(str(spin.cget("state")), tk.DISABLED)


if __name__ == "__main__":
    unittest.main()
