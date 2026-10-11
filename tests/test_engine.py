# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the engine and for the application started whole.

The application tests open the real root window: they need a display and
skip themselves without one. Run under xvfb-run.
"""

import os
import shutil
import sqlite3
import tempfile
import unittest

from engine import Engine
from log import Log
from version import SCHEMA_VERSION

HAS_DISPLAY = bool(os.environ.get("DISPLAY"))

if HAS_DISPLAY:
    from ui.app import App


class EngineTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.log = Log(os.devnull)

    def tearDown(self):
        shutil.rmtree(self.folder)

    def get_path(self):
        return os.path.join(self.folder, "diary.sl3")

    def test_new_file_becomes_an_empty_diary(self):
        engine = Engine(self.get_path(), self.log)
        self.assertEqual(engine.get_schema_version(), SCHEMA_VERSION)
        self.assertEqual(engine.get_reading_count(), 0)
        engine.db.close()

    def test_diary_is_opened_again_as_it_is(self):
        engine = Engine(self.get_path(), self.log)
        engine.db.write("INSERT INTO readings (position_id, recorded_at,"
                        " systolic_mmhg, diastolic_mmhg, heart_rate_bpm)"
                        " VALUES (1, '2026-10-11 08:00:00', 128, 79, 66)")
        engine.db.close()
        engine = Engine(self.get_path(), self.log)
        self.assertEqual(engine.get_reading_count(), 1)
        engine.db.close()

    def test_other_schema_version_is_refused(self):
        con = sqlite3.connect(self.get_path())
        con.execute("PRAGMA user_version = 99")
        con.close()
        with self.assertRaises(ValueError):
            Engine(self.get_path(), self.log)

    def test_setting_is_read(self):
        engine = Engine(":memory:", self.log)
        self.assertEqual(engine.get_setting("systolic_threshold_mmhg"), "135")

    def test_missing_setting_is_an_error_not_none(self):
        engine = Engine(":memory:", self.log)
        with self.assertRaises(ValueError):
            engine.get_setting("nothing")


@unittest.skipUnless(HAS_DISPLAY, "no display")
class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = App(database=":memory:", log=Log(os.devnull),
                       theme="clam")
        self.app.update()

    def tearDown(self):
        if self.app.winfo_exists():
            self.app.destroy()

    def test_class_name_is_one_lowercase_word(self):
        self.assertEqual(self.app.winfo_class(), "Sphygmus")

    def test_status_bar_counts_the_readings(self):
        self.assertEqual(self.app.main.status.get(),
                         "0 readings in the diary")

    def test_status_bar_follows_a_new_reading(self):
        engine = self.app.engine
        reading_id = engine.db.write(
            "INSERT INTO readings (position_id, recorded_at, systolic_mmhg,"
            " diastolic_mmhg, heart_rate_bpm)"
            " VALUES (1, '2026-10-11 08:00:00', 128, 79, 66)")
        engine.events.notify("readings", reading_id)
        self.assertEqual(self.app.main.status.get(),
                         "1 readings in the diary")

    def test_closed_main_stops_listening(self):
        self.app.main.destroy()
        self.assertEqual(self.app.engine.events.subscribers["readings"], [])

    def test_unknown_theme_is_refused(self):
        with self.assertRaises(ValueError):
            App(database=":memory:", log=Log(os.devnull), theme="nothing")


if __name__ == "__main__":
    unittest.main()
