# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The engine: it owns the parts, and knows no window.

Composition: the engine *has* a log, a database, the widget tools and the
events, as attributes, so a call says who does the work:
self.engine.db.read(...), self.engine.events.notify(...). It inherits from
nothing.

It is built by the application with what main() read from the outside world
- where the diary is, and the log - and asks nothing of the outside world
itself.
"""

import os

from dbms import DBMS
from events import Events
from tools import Tools
from version import SCHEMA_VERSION

# The folder of this file: the .sql files that build a new diary are here.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# The files that build an empty diary, in this order.
SCRIPTS = (os.path.join("sql", "ddl", "001_schema.sql"),
           os.path.join("sql", "dml", "001_master_data.sql"))


class Engine:
    """The parts of the program, and the questions about the diary."""

    def __init__(self, database, log):
        self.log = log
        self.tools = Tools()
        self.events = Events(log)
        self.db = DBMS(database, log)
        self.set_schema()
        self.log.trace("engine ready on {0}".format(database))

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
            path = os.path.join(PROJECT_DIR, name)
            with open(path, "r", encoding="utf-8") as f:
                self.db.write_script(f.read())
            self.log.trace("built from {0}".format(name))

    def get_setting(self, code):
        """The value of a setting, as text. A missing one is an error."""
        sql = "SELECT value FROM settings WHERE code = ? AND enable = 1"
        row = self.db.read(False, sql, (code,))
        if row is None:
            raise ValueError("no setting {0}".format(code))
        return row["value"]

    def get_reading_count(self):
        sql = "SELECT COUNT(*) AS n FROM readings WHERE enable = 1"
        row = self.db.read(False, sql)
        return row["n"]
