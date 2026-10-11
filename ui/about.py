# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""About: what the program is, who wrote it, what it runs on.

The versions are asked of what is running, not written down: Python, Tk,
the SQLite library behind the connection, ReportLab if it is there. When
something misbehaves on a machine, this window is the first thing to read
out over the phone.
"""

import platform
import tkinter as tk
import webbrowser
from tkinter import ttk

from report import REPORTLAB_VERSION
from version import (APP_NAME, __author__, __date__, __license__,
                     __version__)

# Where the source lives. Opened with webbrowser, from the standard library.
SOURCE = "https://github.com/1966bc/sphygmus"


class About(tk.Toplevel):
    """The icon, the name, the facts; Licence and Close."""

    def __init__(self, parent, on_licence):
        super().__init__(parent, name="about")
        self.engine = self.nametowidget(".").engine
        # Handed in by the main window, which opens the licence through the
        # register of windows like any other.
        self.on_licence = on_licence
        self.facts = self.get_facts()

        self.transient(parent.winfo_toplevel())
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.engine.tools.hide_me(self)
        self.init_ui()
        self.bind("<Escape>", self.on_cancel)

    def get_facts(self):
        """(label, value) in the order they are shown."""
        reportlab = REPORTLAB_VERSION
        if reportlab is None:
            reportlab = "not installed: no report"
        diary = self.engine.db.database
        if self.engine.is_demo():
            diary = "the demo diary, invented readings"
        return (("Version", "{0}, {1}".format(__version__, __date__)),
                ("Author", __author__),
                ("Licence", __license__),
                ("Python", platform.python_version()),
                ("Tk", str(self.tk.call("info", "patchlevel"))),
                ("SQLite", self.engine.db.get_sqlite_version()),
                ("ReportLab", reportlab),
                ("Diary", diary))

    def init_ui(self):
        frm_main = ttk.Frame(self, style="App.TFrame", padding=16)

        # The 64 pixel icon, already loaded by the root window: an image
        # belongs to the Tk that made it, and that one is ours.
        root = self.nametowidget(".")
        ttk.Label(frm_main, image=root.icons[3]).grid(
            row=0, column=0, rowspan=2, sticky=tk.N, padx=(0, 12))
        ttk.Label(frm_main, text=APP_NAME, style="Title.TLabel").grid(
            row=0, column=1, sticky=tk.W)
        ttk.Label(frm_main, style="App.TLabel",
                  text="A home blood pressure diary. It records and shows;"
                       " it does not diagnose.").grid(row=1, column=1,
                                                      sticky=tk.W)
        ttk.Separator(frm_main).grid(row=2, column=0, columnspan=2,
                                     sticky=tk.EW, pady=12)

        frm_facts = ttk.Frame(frm_main, style="App.TFrame")
        for row, (label, value) in enumerate(self.facts):
            self.add_fact(frm_facts, row, label, value)
        link = self.add_fact(frm_facts, len(self.facts), "Source", SOURCE)
        link.configure(style="Link.TLabel", cursor="hand2")
        link.bind("<Button-1>", self.on_source)
        frm_facts.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        buttons = self.engine.tools.get_button_column(
            frm_main, (("Licence", self.on_licence),
                       ("Close", self.on_cancel)), window=self)
        buttons.grid(row=0, column=2, rowspan=4, sticky=tk.N,
                     padx=(16, 0))

        frm_main.pack(fill=tk.BOTH, expand=1)

    def add_fact(self, container, row, label, value):
        ttk.Label(container, text=label, style="App.TLabel").grid(
            row=row, column=0, sticky=tk.W)
        fact = ttk.Label(container, text=value, style="App.TLabel")
        fact.grid(row=row, column=1, sticky=tk.W, padx=(12, 0))
        return fact

    def on_open(self):
        """Show it in place; called by the register of windows."""
        self.title("About {0}".format(APP_NAME))
        self.engine.tools.center_me(self, self.master)

    def on_source(self, evt=None):
        webbrowser.open(SOURCE)

    def on_cancel(self, evt=None):
        self.destroy()
