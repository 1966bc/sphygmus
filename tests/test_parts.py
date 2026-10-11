# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the parts the engine is made of: Config, Log, Events, DBMS."""

import os
import shutil
import sqlite3
import tempfile
import unittest

from config import Config
from dbms import DBMS
from events import Events
from log import Log


class FolderTestCase(unittest.TestCase):
    """A folder of its own for each test, removed afterwards."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.folder)

    def get_path(self, name, text=None):
        path = os.path.join(self.folder, name)
        if text is not None:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        return path


class ConfigTestCase(FolderTestCase):

    def test_value_is_read(self):
        path = self.get_path("a.ini", "; note\n[database]\npath = d.sl3\n")
        self.assertEqual(Config(path).get("database", "path"), "d.sl3")

    def test_value_may_hold_an_equals_sign(self):
        path = self.get_path("a.ini", "[s]\nk = a=b\n")
        self.assertEqual(Config(path).get("s", "k"), "a=b")

    def test_line_outside_a_section_is_refused(self):
        path = self.get_path("a.ini", "path = d.sl3\n")
        with self.assertRaises(ValueError):
            Config(path)

    def test_line_without_equals_is_refused(self):
        path = self.get_path("a.ini", "[s]\npath\n")
        with self.assertRaises(ValueError):
            Config(path)

    def test_key_twice_is_refused(self):
        path = self.get_path("a.ini", "[s]\nk = 1\nk = 2\n")
        with self.assertRaises(ValueError):
            Config(path)

    def test_missing_key_is_an_error_not_none(self):
        path = self.get_path("a.ini", "[s]\nk = 1\n")
        with self.assertRaises(ValueError):
            Config(path).get("s", "other")


class LogTestCase(FolderTestCase):

    def test_error_is_written(self):
        log = Log(self.get_path("a.log"))
        log.error("disk on fire")
        with open(log.path, encoding="utf-8") as f:
            self.assertIn("ERROR test_error_is_written: disk on fire",
                          f.read())

    def test_full_file_is_rotated(self):
        log = Log(self.get_path("a.log", "x" * Log.MAX_SIZE))
        log.error("next")
        self.assertTrue(os.path.exists(log.path + ".1"))
        self.assertLess(os.path.getsize(log.path), Log.MAX_SIZE)


class EventsTestCase(unittest.TestCase):

    def setUp(self):
        self.events = Events(Log(os.devnull))
        self.told = []

    def on_readings(self, row_id=None):
        self.told.append(row_id)

    def test_subscriber_is_told_the_row(self):
        self.events.subscribe("readings", self.on_readings)
        self.events.notify("readings", 7)
        self.assertEqual(self.told, [7])

    def test_unsubscribed_is_not_told(self):
        self.events.subscribe("readings", self.on_readings)
        self.events.unsubscribe("readings", self.on_readings)
        self.events.notify("readings", 7)
        self.assertEqual(self.told, [])

    def test_subscribing_twice_tells_once(self):
        self.events.subscribe("readings", self.on_readings)
        self.events.subscribe("readings", self.on_readings)
        self.events.notify("readings", 7)
        self.assertEqual(self.told, [7])

    def test_misspelt_event_is_refused(self):
        with self.assertRaises(ValueError):
            self.events.notify("reading", 7)


class DBMSTestCase(FolderTestCase):

    def setUp(self):
        super().setUp()
        self.log = Log(self.get_path("a.log"))
        self.db = DBMS(":memory:", self.log)
        self.db.write_script("CREATE TABLE notes (note_id INTEGER PRIMARY KEY,"
                             " body TEXT NOT NULL, enable INTEGER);")

    def tearDown(self):
        self.db.close()
        super().tearDown()

    def test_insert_is_built_from_the_schema(self):
        sql, args = self.db.get_insert("notes", {"enable": 1, "body": "a"})
        self.assertEqual(sql, "INSERT INTO notes (body, enable)"
                              " VALUES (?, ?)")
        self.assertEqual(args, ["a", 1])

    def test_missing_column_is_refused(self):
        with self.assertRaises(ValueError):
            self.db.get_insert("notes", {"body": "a"})

    def test_unknown_column_is_refused(self):
        with self.assertRaises(ValueError):
            self.db.get_insert("notes", {"body": "a", "enable": 1,
                                         "colour": "red"})

    def test_update_puts_the_key_last(self):
        sql, args = self.db.get_update("notes", 3, {"body": "b",
                                                    "enable": 0})
        self.assertTrue(sql.endswith("WHERE note_id = ?"))
        self.assertEqual(args, ["b", 0, 3])

    def test_write_returns_the_new_id(self):
        sql, args = self.db.get_insert("notes", {"body": "a", "enable": 1})
        self.assertEqual(self.db.write(sql, args), 1)

    def test_failed_read_raises_and_is_logged(self):
        with self.assertRaises(sqlite3.Error):
            self.db.read(True, "SELECT * FROM nowhere")
        with open(self.log.path, encoding="utf-8") as f:
            self.assertIn("read failed: SELECT * FROM nowhere", f.read())

    def test_failed_write_leaves_nothing(self):
        with self.assertRaises(sqlite3.Error):
            self.db.write("INSERT INTO notes (body) VALUES (NULL)")
        rows = self.db.read(True, "SELECT * FROM notes")
        self.assertEqual(rows, [])

    def test_foreign_keys_are_on(self):
        row = self.db.read(False, "PRAGMA foreign_keys")
        self.assertEqual(row["foreign_keys"], 1)


if __name__ == "__main__":
    unittest.main()
