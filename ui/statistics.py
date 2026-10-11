# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The statistics of the period, one row per position (R5).

Count, mean, minimum and maximum, computed by SQLite when they are shown
(R1). The mean is shown whole: a reading is whole, and a tenth of a mmHg
would claim a precision the device does not have.
"""

import tkinter as tk
from tkinter import ttk


class Statistics(ttk.Frame):
    """A small table: position, readings, systolic, diastolic, heart rate.
    """

    def __init__(self, parent, get_period):
        super().__init__(parent, style="App.TFrame")
        self.engine = self.nametowidget(".").engine
        self.get_period = get_period

        self.init_ui()

        self.engine.events.subscribe("readings", self.on_changed)
        self.bind("<Destroy>", self.on_destroy, add="+")

    def init_ui(self):
        columns = (("#0", "id", tk.W, False, 0, 0),
                   ("#1", "Position", tk.W, True, 70, 80),
                   ("#2", "Readings", tk.CENTER, False, 80, 80),
                   ("#3", "Systolic", tk.CENTER, False, 110, 110),
                   ("#4", "Diastolic", tk.CENTER, False, 110, 110),
                   ("#5", "Heart rate", tk.CENTER, False, 110, 110))
        self.tree = self.engine.tools.get_tree(self, columns,
                                               show="headings")
        self.tree.configure(height=4)

    def get_caption(self, mean, low, high):
        """Mean with its range: 127 (110-142).

        Rounded half up, as a person rounds: format() would round half to
        even, and show a mean of 126.5 as 126.
        """
        return "{0} ({1}-{2})".format(int(mean + 0.5), low, high)

    def set_rows(self):
        self.engine.tools.clear_treeview(self.tree)
        period = self.get_period()
        rows = []
        if period is not None:
            rows = self.engine.get_statistics(*period)
        for row in rows:
            self.tree.insert("", tk.END, iid=str(row["position_id"]),
                             values=(row["position"], row["readings"],
                                     self.get_caption(row["systolic_mean"],
                                                      row["systolic_min"],
                                                      row["systolic_max"]),
                                     self.get_caption(row["diastolic_mean"],
                                                      row["diastolic_min"],
                                                      row["diastolic_max"]),
                                     self.get_caption(row["heart_rate_mean"],
                                                      row["heart_rate_min"],
                                                      row["heart_rate_max"])))

    def on_changed(self, row_id=None):
        self.set_rows()

    def on_destroy(self, evt=None):
        if evt is None or evt.widget is self:
            self.engine.events.unsubscribe("readings", self.on_changed)
