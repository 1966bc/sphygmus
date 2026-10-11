# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The readings of the period, the latest first.

A reading at or over the threshold is shown in the emphasis colour (R4):
computed here, as the row is drawn, and stored nowhere.

Gestures, because they are done to something already on screen: a double
click or Enter opens a reading in its form, to be corrected; Delete takes
it out of the diary. After a save the list lands on the row saved.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from version import APP_NAME


class ReadingList(ttk.Frame):
    """The list, and what can be done to one of its rows."""

    def __init__(self, parent, get_period, on_pick):
        super().__init__(parent, style="App.TFrame")
        self.engine = self.nametowidget(".").engine
        # Handed in by the main window, which owns the period and opens the
        # form: the list asks for the one and hands a row to the other
        # without knowing either.
        self.get_period = get_period
        self.on_pick = on_pick
        self.count = tk.StringVar()

        self.init_ui()

        self.engine.events.subscribe("readings", self.on_changed)
        self.engine.events.subscribe("settings", self.on_changed)
        self.bind("<Destroy>", self.on_destroy, add="+")

    def init_ui(self):
        tools = self.engine.tools
        frame = ttk.Frame(self, style="App.TFrame")
        columns = (("#0", "id", tk.W, False, 0, 0),
                   ("#1", "Date", tk.CENTER, False, 90, 90),
                   ("#2", "Time", tk.CENTER, False, 70, 70),
                   ("#3", "Position", tk.W, True, 70, 80),
                   ("#4", "Systolic", tk.CENTER, False, 80, 80),
                   ("#5", "Diastolic", tk.CENTER, False, 80, 80),
                   ("#6", "Heart rate", tk.CENTER, False, 85, 85))
        self.tree = tools.get_tree(frame, columns, show="headings")
        self.tree.tag_configure("over",
                                foreground=tools.get_rgb(*tools.EMPHASIS))
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Return>", self.on_double_click)
        self.tree.bind("<KP_Enter>", self.on_double_click)
        self.tree.bind("<Delete>", self.on_delete)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        ttk.Label(self, textvariable=self.count,
                  style="App.TLabel").pack(side=tk.TOP, anchor=tk.W)

    def set_rows(self, selected_id=None):
        """Fill the list with the period's readings; land on selected_id."""
        self.engine.tools.clear_treeview(self.tree)
        period = self.get_period()
        rows = []
        if period is not None:
            rows = self.engine.get_readings(*period)
        threshold = self.engine.get_threshold()
        over = 0
        for row in rows:
            tags = ()
            if threshold.is_over(row["systolic_mmhg"],
                                 row["diastolic_mmhg"]):
                tags = ("over",)
                over += 1
            moment = self.engine.get_moment(row["recorded_at"])
            self.tree.insert("", tk.END, iid=str(row["reading_id"]),
                             tags=tags,
                             values=(self.engine.get_shown_day(moment),
                                     moment.strftime("%H:%M:%S"),
                                     row["position"],
                                     row["systolic_mmhg"],
                                     row["diastolic_mmhg"],
                                     row["heart_rate_bpm"]))
        self.count.set("{0} readings, {1} at or over {2}".format(
            len(rows), over, threshold.get_caption()))
        if selected_id is not None and self.tree.exists(str(selected_id)):
            self.engine.tools.set_selected(self.tree, str(selected_id))

    def set_first(self):
        """The keyboard on the list, on the first row if there is one."""
        rows = self.tree.get_children()
        if rows:
            self.engine.tools.set_selected(self.tree, rows[0])
        else:
            self.tree.focus_set()

    def get_selected_id(self):
        """The reading under the focus, or None."""
        iid = self.tree.focus()
        reading_id = None
        if iid:
            reading_id = int(iid)
        return reading_id

    def on_changed(self, row_id=None):
        self.set_rows(row_id)

    def on_double_click(self, evt=None):
        reading_id = self.get_selected_id()
        if reading_id is not None:
            self.on_pick(reading_id)

    def on_delete(self, evt=None):
        """Take a reading out of the diary, once asked (R6).

        It stays in the file and in the trail; it leaves the list, the
        chart, the statistics and the report. A question, because nothing
        on screen brings it back.
        """
        reading_id = self.get_selected_id()
        if reading_id is not None:
            values = self.tree.item(str(reading_id), "values")
            question = ("Remove the reading of {0} {1}, {2}/{3}?\n\nIt"
                        " leaves the diary, the chart and the report.".format(
                            values[0], values[1], values[3], values[4]))
            if messagebox.askyesno(APP_NAME, question,
                                   default=messagebox.NO,
                                   parent=self.winfo_toplevel()):
                self.engine.disable_reading(reading_id)
                self.engine.events.notify("readings", None)

    def on_destroy(self, evt=None):
        if evt is None or evt.widget is self:
            self.engine.events.unsubscribe("readings", self.on_changed)
            self.engine.events.unsubscribe("settings", self.on_changed)
