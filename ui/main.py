# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The main window: the one the diary is kept in.

The period at the top; the readings in one list with the buttons stacked on
its right, New, Edit and Close; the statistics of the period below. A
reading is typed and corrected in its own form, ui/reading.py, opened from
here: the plural opens the singular.

Composition: the window *has* its parts and wires them. The parts do not
know each other. Each subscribes to the events it shows and asks the
period through a function handed to it; the list asks for a reading to be
opened through another.
"""

import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from ui.calendarium import DATE_CHANGED, Calendarium
from ui.reading import Reading
from ui.readings import ReadingList
from ui.settings import Settings
from ui.statistics import Statistics
from version import APP_NAME, __date__, __license__, __version__


class Main(ttk.Frame):
    """The period, the readings and their statistics."""

    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame")
        # The engine lives on the root window; any widget finds it by name.
        self.engine = self.nametowidget(".").engine

        self.status = tk.StringVar()
        # Ticked while the demo diary is open.
        self.demo = tk.BooleanVar(value=False)
        # The days the period was last set to from the settings: a change of
        # threshold must not move a period somebody chose by hand.
        self.period_days = self.engine.get_period_days()

        self.init_menu()
        self.init_ui()

        self.engine.events.subscribe("readings", self.on_readings)
        self.engine.events.subscribe("settings", self.on_settings)
        self.bind("<Destroy>", self.on_destroy, add="+")
        self.set_parts()

    def init_menu(self):
        root = self.nametowidget(".")
        menubar = tk.Menu(root, tearoff=0)

        # The diary as a file, in a menu of its own under File: copies,
        # checks, starting anew.
        database = tk.Menu(menubar, tearoff=0)
        database.add_command(label="Back up", underline=0,
                             command=self.on_backup)
        database.add_command(label="Restore a backup...", underline=0,
                             command=self.on_restore)
        database.add_separator()
        database.add_command(label="Check", underline=0,
                             command=self.on_check)
        database.add_command(label="Vacuum", underline=0,
                             command=self.on_vacuum)
        database.add_separator()
        database.add_command(label="Start a new diary...", underline=6,
                             command=self.on_fresh_diary)

        files = tk.Menu(menubar, tearoff=0)
        files.add_cascade(label="Database", underline=0, menu=database)
        files.add_checkbutton(label="Demo diary", underline=1,
                              variable=self.demo, command=self.on_demo)
        files.add_separator()
        files.add_command(label="Settings...", underline=0,
                          command=self.on_settings_window)
        files.add_separator()
        files.add_command(label="Exit", underline=1, command=root.on_exit)
        menubar.add_cascade(label="File", underline=0, menu=files)

        # The diary as readings.
        diary = tk.Menu(menubar, tearoff=0)
        diary.add_command(label="New reading", underline=0,
                          command=self.on_new)
        menubar.add_cascade(label="Diary", underline=0, menu=diary)

        helper = tk.Menu(menubar, tearoff=0)
        helper.add_command(label="About", underline=0, command=self.on_about)
        menubar.add_cascade(label="Help", underline=0, menu=helper)

        root.configure(menu=menubar)
        self.mnu_file = files
        self.mnu_database = database
        self.mnu_diary = diary
        self.mnu_help = helper

    def init_ui(self):
        root = self.nametowidget(".")

        bar = ttk.Frame(self, style="StatusBar.TFrame")
        ttk.Label(bar, textvariable=self.status,
                  style="StatusBar.TLabel").pack(side=tk.LEFT, padx=4)
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        frm_period = ttk.Frame(self, style="App.TFrame", padding=(8, 8, 8, 0))
        self.start = Calendarium(frm_period, "From")
        self.end = Calendarium(frm_period, "To")
        self.start.set_days_ago(self.period_days)
        self.start.pack(side=tk.LEFT, padx=(0, 8))
        self.end.pack(side=tk.LEFT)
        self.start.bind(DATE_CHANGED, self.on_period)
        self.end.bind(DATE_CHANGED, self.on_period)
        frm_period.pack(side=tk.TOP, fill=tk.X)

        self.statistics = Statistics(self, self.get_period)
        self.statistics.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(0, 8))

        frm_list = ttk.Frame(self, style="App.TFrame", padding=8)
        self.readings = ReadingList(frm_list, self.get_period, self.on_edit)
        self.readings.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        buttons = self.engine.tools.get_button_column(
            frm_list, (("New", self.on_new),
                       ("Edit", self.on_edit),
                       ("Close", root.on_exit)), window=root)
        buttons.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        frm_list.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def get_period(self):
        """The first and last day shown, or None when they do not make one.

        None, and not an exception: a date half typed is a normal state of
        the two fields, and the parts show nothing until it is a date.
        """
        start = self.start.get_date()
        end = self.end.get_date()
        period = None
        if start is not None and end is not None and start <= end:
            period = (start, end)
        return period

    def set_parts(self):
        self.readings.set_rows()
        self.statistics.set_rows()
        self.set_status()

    def set_status(self, message=None):
        """The count and the period; or a message, when there is one."""
        if message is None:
            period = self.get_period()
            if period is None:
                shown = "no period: the two dates do not make one"
            else:
                shown = "from {0} to {1}".format(
                    self.engine.get_shown_day(period[0]),
                    self.engine.get_shown_day(period[1]))
            message = "{0} readings in the diary; showing {1}".format(
                self.engine.get_reading_count(), shown)
        self.status.set(message)

    # --- the form of a reading -----------------------------------------------

    def open_reading(self, reading_id):
        """One form at a time: the one open closes, this one opens."""
        self.engine.windows.replace(
            "reading", lambda: Reading(self.winfo_toplevel(), reading_id))

    def on_new(self, evt=None):
        self.open_reading(None)

    def on_edit(self, reading_id=None):
        """The reading given, or the one selected in the list."""
        if reading_id is None:
            reading_id = self.readings.get_selected_id()
        if reading_id is None:
            self.set_status("Select a reading in the list first.")
        else:
            self.open_reading(reading_id)

    # --- the diary file ------------------------------------------------------

    def on_backup(self, evt=None):
        path = self.engine.backup()
        self.set_status("Backed up to {0}".format(path))

    def on_restore(self, evt=None):
        """Choose a backup and put it in place of the diary, once asked."""
        path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(), title="Restore a backup",
            initialdir=self.engine.get_backup_folder(),
            filetypes=(("Diaries", "*.sl3"), ("All files", "*")))
        if path:
            name = os.path.basename(path)
            question = ("Put {0} in place of the diary?\n\nThe diary in use"
                        " is moved into the backup folder, whole. Nothing is"
                        " deleted.".format(name))
            if messagebox.askyesno(APP_NAME, question,
                                   default=messagebox.NO,
                                   parent=self.winfo_toplevel()):
                self.set_restored(path)

    def set_restored(self, path):
        """Check, then restore; a file that fails the check changes nothing.
        """
        self.set_forms_closed()
        moved = self.engine.restore(path)
        self.set_diary_replaced()
        self.set_status("Restored {0}. The diary was moved to {1}".format(
            os.path.basename(path), moved))

    def on_check(self, evt=None):
        """Read every page of the diary; say so only if something is wrong.
        """
        self.engine.tools.busy(self.winfo_toplevel())
        try:
            result = self.engine.db.check()
        finally:
            self.engine.tools.not_busy(self.winfo_toplevel())
        if result == "ok":
            self.set_status("The diary is sound: every page read, no fault.")
        else:
            messagebox.showerror(APP_NAME,
                                 "The diary is damaged:\n\n{0}\n\nRestore a"
                                 " backup.".format(result),
                                 parent=self.winfo_toplevel())

    def on_vacuum(self, evt=None):
        self.engine.tools.busy(self.winfo_toplevel())
        try:
            saved = self.engine.db.vacuum()
        finally:
            self.engine.tools.not_busy(self.winfo_toplevel())
        self.set_status("Vacuum done: {0} bytes saved.".format(saved))

    def on_fresh_diary(self, evt=None):
        """Put the diary aside and start an empty one, once asked.

        A question, with No as the default: the readings leave the screen
        and only moving a file brings them back. Nothing is deleted.
        """
        question = ("Start a new, empty diary?\n\nThe one in use is moved"
                    " into the backup folder beside it, whole. Nothing is"
                    " deleted.")
        if messagebox.askyesno(APP_NAME, question, default=messagebox.NO,
                               parent=self.winfo_toplevel()):
            self.set_fresh_diary()

    def set_fresh_diary(self):
        self.set_forms_closed()
        path = self.engine.set_fresh_diary()
        self.set_diary_replaced()
        self.set_status("New diary. The old one is {0}".format(path))

    def on_demo(self, evt=None):
        """Open the demo diary, or close it and go back to the diary.

        The menu entry is a check box: ticking it has already happened when
        this runs, so the variable says where to go.
        """
        self.set_forms_closed()
        self.engine.tools.busy(self.winfo_toplevel())
        try:
            if self.demo.get():
                self.engine.set_demo()
            else:
                self.engine.set_home()
        finally:
            self.engine.tools.not_busy(self.winfo_toplevel())
        self.nametowidget(".").set_title()
        self.set_diary_replaced()
        if self.engine.is_demo():
            self.set_status("Demo diary: invented readings. Untick File >"
                            " Demo diary to go back to yours.")
        else:
            self.set_status("Back on your diary.")

    def set_forms_closed(self):
        """The forms open belong to the diary that is going."""
        for name in ("reading", "settings"):
            window = self.engine.windows.get(name)
            if window is not None:
                window.on_cancel()

    def set_diary_replaced(self):
        """Everything on screen is read again from the new file."""
        self.engine.events.notify("settings", None)
        self.engine.events.notify("readings", None)
        self.readings.set_first()

    # --- events --------------------------------------------------------------

    def on_period(self, evt=None):
        self.set_parts()

    def on_readings(self, row_id=None):
        self.set_status()

    def on_settings(self, row_id=None):
        """Move the period only if its number of days changed."""
        days = self.engine.get_period_days()
        if days != self.period_days:
            self.period_days = days
            self.start.set_days_ago(days)
            self.end.set_today()
            self.set_parts()

    def on_settings_window(self, evt=None):
        self.engine.windows.show(
            "settings", lambda: Settings(self.winfo_toplevel()))

    def on_about(self, evt=None):
        messagebox.showinfo(
            APP_NAME,
            "{0} {1}, {2}\n\nA home blood pressure diary.\nIt records and"
            " shows; it does not diagnose.\n\nGiuseppe Costanzi (1966bc)\n"
            "{3}".format(APP_NAME, __version__, __date__, __license__),
            parent=self.winfo_toplevel())

    def on_destroy(self, evt=None):
        # <Destroy> arrives for every child too: only this frame's counts.
        if evt is None or evt.widget is self:
            self.engine.events.unsubscribe("readings", self.on_readings)
            self.engine.events.unsubscribe("settings", self.on_settings)
