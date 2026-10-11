# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The chart window: the period's readings, drawn.

A window of its own, so the main window keeps the list whole and the chart
can be made as large as the screen. One at a time, through the register of
windows with show. It reads the readings and hands numbers to the canvas,
which draws them knowing nothing of the diary.

It follows what it shows: readings saved or removed, a new threshold, and
the period of the main window, which it asks through a function handed to
it - the main window tells it when the period moves.
"""

import tkinter as tk
from tkinter import ttk

from ui.pressure_canvas import PressureCanvas
from version import APP_NAME


class Chart(tk.Toplevel):
    """A canvas, and Close."""

    def __init__(self, parent, get_period):
        super().__init__(parent, name="chart")
        self.engine = self.nametowidget(".").engine
        self.get_period = get_period

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.engine.tools.hide_me(self)
        self.init_ui()
        self.bind("<Escape>", self.on_cancel)

        self.engine.events.subscribe("readings", self.on_changed)
        self.engine.events.subscribe("settings", self.on_changed)
        self.bind("<Destroy>", self.on_destroy, add="+")

    def init_ui(self):
        frm_main = ttk.Frame(self, style="App.TFrame", padding=8)
        self.canvas = PressureCanvas(frm_main)
        buttons = self.engine.tools.get_button_column(
            frm_main, (("Close", self.on_cancel),), window=self)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        buttons.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        frm_main.pack(fill=tk.BOTH, expand=1)

    def on_open(self):
        """Draw and show; called by the register of windows."""
        self.set_drawn()
        self.engine.tools.center_me(self, self.master)

    def set_drawn(self):
        """Read the period's readings and hand them to the canvas."""
        period = self.get_period()
        readings = []
        caption = "no period"
        if period is not None:
            caption = "from {0} to {1}".format(
                self.engine.get_shown_day(period[0]),
                self.engine.get_shown_day(period[1]))
            for row in self.engine.get_readings(*period):
                readings.append((self.engine.get_moment(row["recorded_at"]),
                                 row["position_id"], row["systolic_mmhg"],
                                 row["diastolic_mmhg"]))
        self.title("{0} - chart {1}".format(APP_NAME, caption))
        self.canvas.set_data(readings, self.engine.get_threshold(), period)

    def on_changed(self, row_id=None):
        self.set_drawn()

    def on_cancel(self, evt=None):
        self.destroy()

    def on_destroy(self, evt=None):
        # However the window goes - Close, the X, the program ending - it
        # stops listening, or it is called on a canvas that is gone.
        if evt is None or evt.widget is self:
            self.engine.events.unsubscribe("readings", self.on_changed)
            self.engine.events.unsubscribe("settings", self.on_changed)
