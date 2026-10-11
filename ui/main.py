# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The main window: the one the diary is kept in.

Composition: it *has* its parts - the entry strip at the top, the period,
the list and the statistics - and wires them. The parts do not know each
other. Each subscribes to the events it shows; the period they ask of the
main window through a function handed to them, and a double click on the
list reaches the entry strip through another.

What is done every day has a gesture: Enter in the strip, a double click or
Delete on the list. What is done now and then is in the menu.
"""

import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from ui.calendarium import DATE_CHANGED, Calendarium
from ui.entry import EntryStrip
from ui.readings import ReadingList
from ui.statistics import Statistics
from version import APP_NAME, __date__, __license__, __version__

# The period shown when the program starts: the last month, which is about
# what a doctor asks to see.
DEFAULT_DAYS = 30


class Main(ttk.Frame):
    """The entry strip, the period, the readings and their statistics."""

    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame")
        # The engine lives on the root window; any widget finds it by name.
        self.engine = self.nametowidget(".").engine

        self.status = tk.StringVar()

        self.init_menu()
        self.init_ui()

        self.engine.events.subscribe("readings", self.on_readings)
        self.bind("<Destroy>", self.on_destroy, add="+")
        self.set_parts()

    def init_menu(self):
        root = self.nametowidget(".")
        menubar = tk.Menu(root, tearoff=0)

        diary = tk.Menu(menubar, tearoff=0)
        diary.add_command(label="Quit", underline=0, command=root.on_exit)
        menubar.add_cascade(label="Diary", underline=0, menu=diary)

        helper = tk.Menu(menubar, tearoff=0)
        helper.add_command(label="About", underline=0, command=self.on_about)
        menubar.add_cascade(label="Help", underline=0, menu=helper)

        root.configure(menu=menubar)
        self.menubar = menubar
        self.mnu_diary = diary
        self.mnu_help = helper

    def init_ui(self):
        bar = ttk.Frame(self, style="StatusBar.TFrame")
        ttk.Label(bar, textvariable=self.status,
                  style="StatusBar.TLabel").pack(side=tk.LEFT, padx=4)
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.entry = EntryStrip(self)
        self.entry.pack(side=tk.TOP, fill=tk.X)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(side=tk.TOP,
                                                       fill=tk.X, pady=4)

        frm_period = ttk.Frame(self, style="App.TFrame", padding=(8, 0))
        self.start = Calendarium(frm_period, "From")
        self.end = Calendarium(frm_period, "To")
        self.start.set_days_ago(DEFAULT_DAYS)
        self.start.pack(side=tk.LEFT, padx=4)
        self.end.pack(side=tk.LEFT, padx=4)
        self.start.bind(DATE_CHANGED, self.on_period)
        self.end.bind(DATE_CHANGED, self.on_period)
        frm_period.pack(side=tk.TOP, fill=tk.X)

        frm_bottom = ttk.Frame(self, style="App.TFrame", padding=(8, 0, 8, 8))
        self.readings = ReadingList(frm_bottom, self.get_period,
                                    self.entry.set_correction)
        self.readings.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.statistics = Statistics(frm_bottom, self.get_period)
        self.statistics.pack(side=tk.LEFT, anchor=tk.N, padx=(8, 0))
        frm_bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

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

    def set_status(self):
        period = self.get_period()
        if period is None:
            shown = "no period: the two dates do not make one"
        else:
            shown = "from {0} to {1}".format(
                self.engine.get_shown_day(period[0]),
                self.engine.get_shown_day(period[1]))
        self.status.set("{0} readings in the diary; showing {1}".format(
            self.engine.get_reading_count(), shown))

    def on_period(self, evt=None):
        self.set_parts()

    def on_readings(self, row_id=None):
        self.set_status()

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
