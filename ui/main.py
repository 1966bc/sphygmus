# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The main window: for now, the status bar alone.

The entry strip, the chart, the list and the statistics will be parts of it,
each subscribed to the events it shows.
"""

import tkinter as tk
from tkinter import ttk


class Main(ttk.Frame):
    """The one window the diary is kept in."""

    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame")
        # The engine lives on the root window; any widget finds it by name.
        self.engine = self.nametowidget(".").engine

        self.status = tk.StringVar()
        self.init_ui()

        self.engine.events.subscribe("readings", self.on_readings)
        self.bind("<Destroy>", self.on_destroy, add="+")
        self.set_status()

    def init_ui(self):
        bar = ttk.Frame(self, style="StatusBar.TFrame")
        ttk.Label(bar, textvariable=self.status,
                  style="StatusBar.TLabel").pack(side=tk.LEFT, padx=4)
        bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self):
        count = self.engine.get_reading_count()
        self.status.set("{0} readings in the diary".format(count))

    def on_readings(self, row_id=None):
        self.set_status()

    def on_destroy(self, evt=None):
        # <Destroy> arrives for every child too: only this frame's counts.
        if evt is None or evt.widget is self:
            self.engine.events.unsubscribe("readings", self.on_readings)
