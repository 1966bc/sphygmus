# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the schema: what the database itself refuses, whoever asks.

A database in memory, built from the same files a real diary is built from.
"""

import os
import sqlite3
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = (os.path.join(ROOT, "sql", "ddl", "001_schema.sql"),
           os.path.join(ROOT, "sql", "dml", "001_master_data.sql"))

INSERT = ("INSERT INTO readings (position_id, recorded_at, systolic_mmhg,"
          " diastolic_mmhg, heart_rate_bpm) VALUES (?, ?, ?, ?, ?)")

SEATED = 1


class SchemaTestCase(unittest.TestCase):

    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.execute("PRAGMA foreign_keys = ON")
        for path in SCRIPTS:
            with open(path, encoding="utf-8") as f:
                self.con.executescript(f.read())

    def tearDown(self):
        self.con.close()

    def add(self, recorded_at, systolic=128, diastolic=79, rate=66,
            position=SEATED):
        cur = self.con.execute(INSERT, (position, recorded_at, systolic,
                                        diastolic, rate))
        return cur.lastrowid

    def get_trail(self):
        sql = ("SELECT reading_id, operation FROM audit_readings"
               " ORDER BY audit_reading_id")
        return self.con.execute(sql).fetchall()

    # --- what a reading must be ----------------------------------------------

    def test_schema_version_is_one(self):
        version = self.con.execute("PRAGMA user_version").fetchone()[0]
        self.assertEqual(version, 1)

    def test_valid_reading_is_stored(self):
        self.add("2026-10-11 08:00:00")
        count = self.con.execute("SELECT COUNT(*) FROM readings").fetchone()
        self.assertEqual(count[0], 1)

    def test_italian_date_is_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.add("11/10/2026 08:00")

    def test_date_without_seconds_is_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.add("2026-10-11 08:00")

    def test_systolic_below_diastolic_is_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.add("2026-10-11 08:00:00", systolic=79, diastolic=128)

    def test_zero_heart_rate_is_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.add("2026-10-11 08:00:00", rate=0)

    def test_unknown_position_is_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.add("2026-10-11 08:00:00", position=99)

    def test_two_readings_in_one_second_are_refused(self):
        self.add("2026-10-11 08:00:00")
        with self.assertRaises(sqlite3.IntegrityError):
            self.add("2026-10-11 08:00:00", systolic=130)

    # --- R6: nothing deleted, nothing changed --------------------------------

    def test_delete_is_refused(self):
        reading_id = self.add("2026-10-11 08:00:00")
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("DELETE FROM readings WHERE reading_id = ?",
                             (reading_id,))

    def test_changing_a_value_is_refused(self):
        reading_id = self.add("2026-10-11 08:00:00")
        sql = "UPDATE readings SET systolic_mmhg = 120 WHERE reading_id = ?"
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(sql, (reading_id,))

    def test_correction_reuses_the_second(self):
        old_id = self.add("2026-10-11 08:00:00")
        self.con.execute("UPDATE readings SET enable = 0"
                         " WHERE reading_id = ?", (old_id,))
        new_id = self.add("2026-10-11 08:00:00", systolic=120)
        self.assertNotEqual(old_id, new_id)

    # --- the trail -----------------------------------------------------------

    def test_trail_records_a_correction(self):
        old_id = self.add("2026-10-11 08:00:00")
        self.con.execute("UPDATE readings SET enable = 0"
                         " WHERE reading_id = ?", (old_id,))
        new_id = self.add("2026-10-11 08:00:00", systolic=120)
        self.assertEqual(self.get_trail(), [(old_id, "INSERT"),
                                            (old_id, "DISABLE"),
                                            (new_id, "INSERT")])

    def test_trail_records_enable_again(self):
        reading_id = self.add("2026-10-11 08:00:00")
        self.con.execute("UPDATE readings SET enable = 0"
                         " WHERE reading_id = ?", (reading_id,))
        self.con.execute("UPDATE readings SET enable = 1"
                         " WHERE reading_id = ?", (reading_id,))
        self.assertEqual(self.get_trail()[-1], (reading_id, "ENABLE"))

    def test_trail_ignores_enable_unchanged(self):
        reading_id = self.add("2026-10-11 08:00:00")
        self.con.execute("UPDATE readings SET enable = 1"
                         " WHERE reading_id = ?", (reading_id,))
        self.assertEqual(self.get_trail(), [(reading_id, "INSERT")])

    # --- master data ---------------------------------------------------------

    def test_thresholds_are_esh_home(self):
        sql = "SELECT code, value FROM settings WHERE code LIKE '%threshold%'"
        rows = dict(self.con.execute(sql).fetchall())
        self.assertEqual(rows, {"systolic_threshold_mmhg": "135",
                                "diastolic_threshold_mmhg": "85"})

    def test_no_person_is_named(self):
        sql = "SELECT value FROM settings WHERE code = 'patient_name'"
        self.assertEqual(self.con.execute(sql).fetchone()[0], "")


if __name__ == "__main__":
    unittest.main()
