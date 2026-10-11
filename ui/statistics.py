# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The statistics of the period, one line per position (R5).

Count, mean, minimum and maximum, computed by SQLite when they are shown
(R1). Labels on a grid and not a second list: there is nothing in it to
select, and two or three lines read better as a small table than as rows
to scroll.

The mean is shown whole: a reading is whole, and a tenth of a mmHg would
claim a precision the device does not have.
"""

import tkinter as tk
from tkinter import ttk

HEADINGS = ("Position", "Readings", "Systolic", "Diastolic", "Heart rate")


class Statistics(ttk.LabelFrame):
    """Position, readings, then mean (min-max) of the three values."""

    def __init__(self, parent, get_period):
        super().__init__(parent, text="Statistics of the period",
                         style="App.TLabelframe", padding=(8, 2))
        self.engine = self.nametowidget(".").engine
        self.get_period = get_period
        # The lines on show, as text, so a test reads what a person reads.
        self.lines = []

        self.engine.events.subscribe("readings", self.on_changed)
        self.bind("<Destroy>", self.on_destroy, add="+")

    def get_caption(self, mean, low, high):
        """Mean with its range: 127 (110-142).

        Rounded half up, as a person rounds: format() would round half to
        even, and show a mean of 126.5 as 126.
        """
        return "{0} ({1}-{2})".format(int(mean + 0.5), low, high)

    def get_lines(self):
        period = self.get_period()
        rows = []
        if period is not None:
            rows = self.engine.get_statistics(*period)
        lines = []
        for row in rows:
            lines.append((row["position"], str(row["readings"]),
                          self.get_caption(row["systolic_mean"],
                                           row["systolic_min"],
                                           row["systolic_max"]),
                          self.get_caption(row["diastolic_mean"],
                                           row["diastolic_min"],
                                           row["diastolic_max"]),
                          self.get_caption(row["heart_rate_mean"],
                                           row["heart_rate_min"],
                                           row["heart_rate_max"])))
        return lines

    def set_rows(self):
        for child in self.winfo_children():
            child.destroy()
        self.lines = self.get_lines()
        if self.lines:
            self.set_grid([HEADINGS] + self.lines)
        else:
            ttk.Label(self, text="No readings in the period.",
                      style="App.TLabel").grid(row=0, column=0, sticky=tk.W)

    def set_grid(self, lines):
        for row, line in enumerate(lines):
            for column, text in enumerate(line):
                anchor = tk.E
                if column == 0:
                    anchor = tk.W
                ttk.Label(self, text=text, style="App.TLabel",
                          anchor=anchor).grid(row=row, column=column,
                                              sticky=tk.EW, padx=(0, 16))

    def on_changed(self, row_id=None):
        self.set_rows()

    def on_destroy(self, evt=None):
        if evt is None or evt.widget is self:
            self.engine.events.unsubscribe("readings", self.on_changed)
