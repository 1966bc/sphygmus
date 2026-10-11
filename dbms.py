# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The database, and what can be asked of it.

One SQLite file. There is no host, no port, no user and no password: the
diary is the file, and whoever can open the file is in.

A failed statement is written to the log and raised again. It never comes
back as an empty result: a read that fails must not look like a table with
no rows in it.

Taken from Biovarase's dbms.py, less what belonged to its schema (the
session row its triggers read) and its date converters: every date here is
ISO text in a TEXT column, and nothing has to be converted on the way.
"""

import sqlite3


class DBMS:
    """Connection to the database, and the statements built from its schema.
    """

    def __init__(self, database, log):
        # Both are given by whoever creates the object: the application
        # passes the diary and its Log, a test passes ":memory:" and a log
        # of its own.
        self.database = database
        self.log = log
        # table -> its columns as get_table_info returns them, remembered
        # after the first time they are asked of the schema.
        self.dict_tables = {}
        self.set_connection()

    def set_connection(self):
        """Open the database and say how rows come back.

        Foreign keys are off by default in SQLite and have to be asked for
        on every connection, or the constraints are decorative.
        """
        self.con = sqlite3.connect(self.database,
                                   isolation_level="IMMEDIATE")
        # Every row can be read by column name, row["systolic_mmhg"], and not
        # only by position, row[3], which silently changes meaning the day a
        # column is added.
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON")

    def close(self):
        """Close the connection. The file stays where it is."""
        self.con.close()

    def read(self, fetch, sql, args=()):
        """Run a SELECT and return its rows.

        fetch True returns a list, empty when no row matched. fetch False
        returns one row or None. A failed query is written to the log, with
        the statement, and raised again.
        """
        cur = self.con.cursor()
        try:
            cur.execute(sql, args)
            if fetch is True:
                rs = cur.fetchall()
            else:
                rs = cur.fetchone()
        except sqlite3.Error:
            self.log.error("read failed: {0}".format(sql))
            raise
        finally:
            cur.close()

        return rs

    def write(self, sql, args=()):
        """Run one statement and commit it; return the id of the new row.

        On an UPDATE there is no new row: the number of rows touched is what
        the caller wants, so that is what comes back. A failed statement is
        rolled back, written to the log and raised again.
        """
        cur = self.con.cursor()
        try:
            cur.execute(sql, args)
            self.con.commit()
            if sql.lstrip()[:6].upper() == "INSERT":
                written = cur.lastrowid
            else:
                written = cur.rowcount
        except sqlite3.Error:
            self.con.rollback()
            self.log.error("write failed, rolled back: {0}".format(sql))
            raise
        finally:
            cur.close()

        return written

    def write_all(self, statements):
        """Run several statements as one: all of them, or none.

        statements is a sequence of (sql, args). A correction is two
        statements, a disable and an insert, and half of it would leave the
        diary with no reading or with two. Returns what write() would have
        returned for the last one.
        """
        if not statements:
            raise ValueError("a transaction with no statement in it")
        cur = self.con.cursor()
        try:
            for sql, args in statements:
                cur.execute(sql, args)
            if sql.lstrip()[:6].upper() == "INSERT":
                written = cur.lastrowid
            else:
                written = cur.rowcount
            self.con.commit()
        except sqlite3.Error:
            self.con.rollback()
            self.log.error("transaction failed, rolled back: {0}".format(sql))
            raise
        finally:
            cur.close()

        return written

    def backup(self, path):
        """Copy the open database into a new file at path.

        SQLite's own backup, page by page: a copy of the file with the
        operating system could catch it in the middle of a write.
        """
        target = sqlite3.connect(path)
        try:
            self.con.backup(target)
        finally:
            target.close()

    def write_script(self, script):
        """Run a whole .sql file: the schema and the master data.

        executescript commits whatever is pending first and runs the file
        as it is, comments and all: it is how sqlite3 at the shell would
        read it, so the file that builds a diary here is the same one a
        reader can run by hand.
        """
        try:
            self.con.executescript(script)
        except sqlite3.Error:
            self.con.rollback()
            self.log.error("script failed, rolled back")
            raise

    def get_dict(self, row):
        """A row as a dictionary; None stays None."""
        found = None
        if row is not None:
            found = dict(row)
        return found

    def get_table_info(self, table):
        """What a table is made of, asked of the schema once and remembered.

        PRAGMA table_info says, for every column, its name and whether it is
        the primary key: nothing is guessed from the order of the columns.
        Memoization by hand; functools.lru_cache would do it too.
        """
        if table not in self.dict_tables:
            rows = self.read(True, "PRAGMA table_info({0})".format(table))
            if not rows:
                raise ValueError("no table {0}".format(table))
            self.dict_tables[table] = [(row["name"], bool(row["pk"]))
                                       for row in rows]
        return self.dict_tables[table]

    def get_primary_key(self, table):
        """The primary key column of a table, asked of the schema."""
        keys = [name for name, is_key in self.get_table_info(table)
                if is_key]
        if len(keys) != 1:
            raise ValueError("{0} has {1} primary key columns, not one".format(
                table, len(keys)))
        return keys[0]

    def get_fields(self, table):
        """Column names of a table, primary key excluded, in table order."""
        return tuple(name for name, is_key in self.get_table_info(table)
                     if not is_key)

    def get_args(self, table, values):
        """The values of a row as a list, in the order the schema declares.

        values is a dictionary keyed by column name, so no window has to
        know the order of the columns. A missing column and an unknown one
        are both refused, naming the table.
        """
        fields = self.get_fields(table)
        missing = [name for name in fields if name not in values]
        unknown = [name for name in values if name not in fields]
        if missing or unknown:
            raise ValueError("{0}: missing {1}, not a column {2}".format(
                table, missing, unknown))
        return [values[name] for name in fields]

    def get_insert(self, table, values):
        """An INSERT and its args, with the values given by column name."""
        fields = self.get_fields(table)
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(
            table, ", ".join(fields), ", ".join("?" * len(fields)))
        return (sql, self.get_args(table, values))

    def get_update(self, table, key_value, values):
        """An UPDATE and its args, with the values given by column name.

        The primary key is asked of the schema and its value goes last.
        """
        assignments = ", ".join("{0} = ?".format(name)
                                for name in self.get_fields(table))
        sql = "UPDATE {0} SET {1} WHERE {2} = ?".format(
            table, assignments, self.get_primary_key(table))
        args = self.get_args(table, values)
        args.append(key_value)
        return (sql, args)
