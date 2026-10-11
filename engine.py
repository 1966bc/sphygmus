# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The engine: it owns the parts, and knows no window.

Composition: the engine *has* a log, a database, the widget tools, the
events and the register of open windows, as attributes, so a call says who
does the work:
self.engine.db.read(...), self.engine.events.notify(...). It inherits from
nothing.

It is built by the application with what main() read from the outside world
- where the diary is, and the log - and asks nothing of the outside world
itself.

Writing is done here and telling is not: whoever asked for a write calls
events.notify afterwards, because only the caller knows whether it was the
last of several.
"""

import datetime
import os

from dbms import DBMS
from events import Events
from pressure.threshold import Threshold
from tools import Tools
from version import SCHEMA_VERSION
from windows import Windows

# The folder of this file: the .sql files that build a new diary are here.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# The files that build an empty diary, in this order.
SCRIPTS = (os.path.join("sql", "ddl", "001_schema.sql"),
           os.path.join("sql", "dml", "001_master_data.sql"))

# Where copies of the diary go: a folder beside it, so they follow the
# diary wherever sphygmus.ini puts it.
BACKUP_DIR = "backup"

# How a moment is written in the diary (R2), and how a day is shown.
STORED = "%Y-%m-%d %H:%M:%S"
SHOWN_DAY = "%d/%m/%Y"


class Engine:
    """The parts of the program, and the questions about the diary."""

    def __init__(self, database, log):
        self.log = log
        self.tools = Tools()
        self.events = Events(log)
        self.windows = Windows(log)
        self.db = DBMS(database, log)
        # name -> the text of sql/dql/<name>.sql, read once.
        self.queries = {}
        self.set_schema()
        self.log.trace("engine ready on {0}".format(database))

    # --- the diary itself ----------------------------------------------------

    def get_schema_version(self):
        row = self.db.read(False, "PRAGMA user_version")
        return row["user_version"]

    def set_schema(self):
        """Build a new diary, or check that this one is the expected kind.

        A file just created by sqlite3.connect has no tables and version 0:
        it is built from the same .sql files a reader can run at the shell.
        A file of another version is refused, and nothing is written to it.
        """
        version = self.get_schema_version()
        if version == 0:
            self.set_new_diary()
        elif version != SCHEMA_VERSION:
            raise ValueError("the diary has schema {0}, this program reads {1}"
                             .format(version, SCHEMA_VERSION))

    def set_new_diary(self):
        for name in SCRIPTS:
            with open(os.path.join(PROJECT_DIR, name), "r",
                      encoding="utf-8") as f:
                self.db.write_script(f.read())
            self.log.trace("built from {0}".format(name))

    def get_backup_path(self, reason):
        """A new file in backup/, beside the diary, named for the moment.

        sphygmus_20261011_083000_copy.sl3: sorted by name, sorted by date,
        and never one over another.
        """
        if self.db.database == ":memory:":
            raise ValueError("a diary in memory has no file to back up")
        folder = os.path.join(os.path.dirname(self.db.database), BACKUP_DIR)
        os.makedirs(folder, exist_ok=True)
        stem = os.path.splitext(os.path.basename(self.db.database))[0]
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(folder, "{0}_{1}_{2}.sl3".format(stem, stamp,
                                                             reason))

    def backup(self):
        """Copy the diary into backup/; return the path of the copy."""
        path = self.get_backup_path("copy")
        self.db.backup(path)
        self.log.trace("backed up to {0}".format(path))
        return path

    def set_fresh_diary(self):
        """Start a new, empty diary; return where the old one went.

        The old file is moved whole into backup/, not copied and removed:
        nothing is deleted (R6), and a diary started by mistake is undone
        by moving the file back.
        """
        path = self.get_backup_path("replaced")
        self.db.close()
        try:
            os.replace(self.db.database, path)
        except OSError:
            # The old diary is where it was: open it again before saying so.
            self.db.set_connection()
            raise
        self.db.dict_tables = {}
        self.db.set_connection()
        self.set_schema()
        self.log.trace("new diary; the old one is {0}".format(path))
        return path

    def get_query(self, name):
        """A named query, from sql/dql: one file, readable at the shell."""
        if name not in self.queries:
            path = os.path.join(PROJECT_DIR, "sql", "dql",
                                "{0}.sql".format(name))
            with open(path, "r", encoding="utf-8") as f:
                self.queries[name] = f.read()
        return self.queries[name]

    # --- moments -------------------------------------------------------------

    def get_bounds(self, start, end):
        """The first and last instant of a period of days, as stored."""
        first = datetime.datetime.combine(start, datetime.time())
        last = datetime.datetime.combine(end, datetime.time(23, 59, 59))
        return (first.strftime(STORED), last.strftime(STORED))

    def get_moment(self, text):
        """A stored moment back as a datetime."""
        return datetime.datetime.strptime(text, STORED)

    def get_stored(self, moment):
        return moment.strftime(STORED)

    def get_shown_day(self, value):
        """A day the way it is read where the diary is kept: 11/10/2026."""
        return value.strftime(SHOWN_DAY)

    def get_shown_moment(self, moment):
        """A moment as it is shown: 11/10/2026 08:00:00."""
        return "{0} {1}".format(self.get_shown_day(moment),
                                moment.strftime("%H:%M:%S"))

    # --- settings ------------------------------------------------------------

    def get_setting(self, code):
        """The value of a setting, as text. A missing one is an error."""
        sql = "SELECT value FROM settings WHERE code = ? AND enable = 1"
        row = self.db.read(False, sql, (code,))
        if row is None:
            raise ValueError("no setting {0}".format(code))
        return row["value"]

    def set_settings(self, values):
        """Change several settings at once: all of them, or none.

        values is {code: value}. The caller notifies "settings".
        """
        sql = "UPDATE settings SET value = ? WHERE code = ?"
        statements = []
        for code, value in values.items():
            self.get_setting(code)
            statements.append((sql, (value, code)))
        self.db.write_all(statements)

    def get_threshold(self):
        return Threshold(self.get_setting("systolic_threshold_mmhg"),
                         self.get_setting("diastolic_threshold_mmhg"))

    # --- readings ------------------------------------------------------------

    def get_positions(self):
        sql = ("SELECT position_id, description FROM positions"
               " WHERE enable = 1 ORDER BY position_id")
        return self.db.read(True, sql)

    def get_last_position_id(self):
        """The position of the latest reading, or the first position.

        A new reading starts where the last one was taken: whoever measures
        lying down in the evening is likely to do it again.
        """
        sql = ("SELECT position_id FROM readings WHERE enable = 1"
               " ORDER BY recorded_at DESC LIMIT 1")
        row = self.db.read(False, sql)
        if row is None:
            position_id = self.get_positions()[0]["position_id"]
        else:
            position_id = row["position_id"]
        return position_id

    def get_readings(self, start, end):
        """The enabled readings of a period of days, the latest first."""
        return self.db.read(True, self.get_query("readings"),
                            self.get_bounds(start, end))

    def get_statistics(self, start, end):
        """Count, mean, minimum and maximum per position, for a period."""
        return self.db.read(True, self.get_query("statistics"),
                            self.get_bounds(start, end))

    def get_reading(self, reading_id):
        sql = "SELECT * FROM readings WHERE reading_id = ?"
        return self.db.read(False, sql, (reading_id,))

    def get_reading_count(self):
        sql = "SELECT COUNT(*) AS n FROM readings WHERE enable = 1"
        row = self.db.read(False, sql)
        return row["n"]

    def is_taken(self, recorded_at, except_id=None):
        """Whether an enabled reading already holds this second.

        Asked before writing, so the person typing is told in words instead
        of meeting the unique index. except_id is the reading being
        corrected, which is about to give its second back.
        """
        sql = ("SELECT reading_id FROM readings"
               " WHERE recorded_at = ? AND enable = 1")
        rows = self.db.read(True, sql, (recorded_at,))
        others = [row for row in rows if row["reading_id"] != except_id]
        return len(others) > 0

    def get_reading_values(self, recorded_at, position_id, systolic_mmhg,
                           diastolic_mmhg, heart_rate_bpm):
        return {"position_id": position_id,
                "recorded_at": recorded_at,
                "systolic_mmhg": systolic_mmhg,
                "diastolic_mmhg": diastolic_mmhg,
                "heart_rate_bpm": heart_rate_bpm,
                "enable": 1}

    def add_reading(self, values):
        """Store a new reading; return its id. The caller notifies."""
        sql, args = self.db.get_insert("readings", values)
        return self.db.write(sql, args)

    def correct_reading(self, reading_id, values):
        """Disable a reading and store its replacement, in one transaction.

        R6: a reading is never changed. Returns the id of the new one.
        """
        disable = ("UPDATE readings SET enable = 0 WHERE reading_id = ?",
                   (reading_id,))
        insert = self.db.get_insert("readings", values)
        return self.db.write_all((disable, insert))

    def disable_reading(self, reading_id):
        """Take a reading out of the diary. It stays in the file (R6)."""
        sql = "UPDATE readings SET enable = 0 WHERE reading_id = ?"
        return self.db.write(sql, (reading_id,))
