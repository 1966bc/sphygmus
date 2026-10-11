# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the engine: building a diary, opening one, refusing one."""

import os
import shutil
import sqlite3
import tempfile
import unittest

from engine import Engine
from log import Log
from version import SCHEMA_VERSION

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


if __name__ == "__main__":
    unittest.main()
