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

    def add_one(self, engine):
        values = engine.get_reading_values("2026-10-11 08:00:00", 1, 128, 79,
                                           66)
        engine.add_reading(values)

    def test_backup_is_a_whole_copy_beside_the_diary(self):
        engine = Engine(self.get_path(), self.log)
        self.add_one(engine)
        path = engine.backup()
        engine.db.close()
        self.assertEqual(os.path.dirname(path),
                         os.path.join(self.folder, "backup"))
        copy = Engine(path, self.log)
        self.assertEqual(copy.get_reading_count(), 1)
        copy.db.close()

    def test_fresh_diary_is_empty_and_the_old_one_is_kept(self):
        engine = Engine(self.get_path(), self.log)
        self.add_one(engine)
        old = engine.set_fresh_diary()
        self.assertEqual(engine.get_reading_count(), 0)
        self.assertEqual(engine.get_setting("systolic_threshold_mmhg"),
                         "135")
        engine.db.close()
        kept = Engine(old, self.log)
        self.assertEqual(kept.get_reading_count(), 1)
        kept.db.close()

    def test_sound_diary_checks_ok(self):
        engine = Engine(self.get_path(), self.log)
        self.assertEqual(engine.db.check(), "ok")
        engine.db.close()

    def test_vacuum_gives_space_back(self):
        engine = Engine(self.get_path(), self.log)
        engine.db.write_script("CREATE TABLE ballast (b BLOB);"
                               " INSERT INTO ballast"
                               " VALUES (zeroblob(1000000));"
                               " DROP TABLE ballast;")
        self.assertGreater(engine.db.vacuum(), 0)
        engine.db.close()

    def test_restore_puts_the_backup_in_place_and_keeps_both(self):
        engine = Engine(self.get_path(), self.log)
        self.add_one(engine)
        copy = engine.backup()
        engine.disable_reading(1)
        moved = engine.restore(copy)
        self.assertEqual(engine.get_reading_count(), 1)
        self.assertTrue(os.path.exists(copy))
        engine.db.close()
        aside = Engine(moved, self.log)
        self.assertEqual(aside.get_reading_count(), 0)
        aside.db.close()

    def test_restore_of_another_schema_changes_nothing(self):
        engine = Engine(self.get_path(), self.log)
        self.add_one(engine)
        other = os.path.join(self.folder, "other.sl3")
        con = sqlite3.connect(other)
        con.execute("PRAGMA user_version = 99")
        con.close()
        with self.assertRaises(ValueError):
            engine.restore(other)
        self.assertEqual(engine.get_reading_count(), 1)
        self.assertFalse(os.path.exists(engine.get_backup_folder()))
        engine.db.close()

    def test_restore_of_a_file_that_is_not_a_database_changes_nothing(self):
        engine = Engine(self.get_path(), self.log)
        self.add_one(engine)
        other = os.path.join(self.folder, "notes.sl3")
        with open(other, "w", encoding="utf-8") as f:
            f.write("not a database at all, but long enough to be read" * 50)
        with self.assertRaises(sqlite3.DatabaseError):
            engine.restore(other)
        self.assertEqual(engine.get_reading_count(), 1)
        engine.db.close()

    def test_asking_about_a_missing_file_does_not_create_it(self):
        engine = Engine(self.get_path(), self.log)
        missing = os.path.join(self.folder, "missing.sl3")
        with self.assertRaises(sqlite3.OperationalError):
            engine.db.get_file_state(missing)
        self.assertFalse(os.path.exists(missing))
        engine.db.close()

    def test_diary_in_memory_has_no_backup(self):
        engine = Engine(":memory:", self.log)
        with self.assertRaises(ValueError):
            engine.backup()


if __name__ == "__main__":
    unittest.main()
