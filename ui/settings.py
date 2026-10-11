# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The settings of the diary: the name on the report, the threshold, the
period shown at start.

They are rows of the settings table, so they travel with the diary file
and a backup carries them. Saved together, in one transaction, and
announced as "settings": the list redraws its marks, the main window moves
its period if the number of days changed.

One window at a time, through the register of windows with show: opening
it again brings the one open to the front.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from pressure.threshold import Threshold
from version import APP_NAME

# The longest period that can be asked for at start, in days: ten years is
# more than any diary, and keeps a typo from asking for a thousand.
MAX_PERIOD_DAYS = 3660

# The name printed on the report: as long as a name gets.
NAME_LENGTH = 60


class Settings(tk.Toplevel):
    """Name, systolic and diastolic threshold, days shown at start."""

    def __init__(self, parent):
        super().__init__(parent, name="settings")
        self.engine = self.nametowidget(".").engine

        self.patient_name = tk.StringVar()
        self.systolic = tk.StringVar()
        self.diastolic = tk.StringVar()
        self.period_days = tk.StringVar()

        self.transient(parent.winfo_toplevel())
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.engine.tools.hide_me(self)
        self.init_ui()
        self.bind("<Return>", self.on_save)
        self.bind("<KP_Enter>", self.on_save)
        self.bind("<Escape>", self.on_cancel)

    def init_ui(self):
        tools = self.engine.tools
        frm_main = ttk.Frame(self, style="App.TFrame", padding=8)
        self.frm_fields = ttk.Frame(frm_main, style="App.TFrame")

        self.ent_name = tools.get_entry(self.frm_fields, self.patient_name)
        self.patient_name.trace_add(
            "write", lambda *args: tools.limit_chars(self.patient_name,
                                                     NAME_LENGTH))
        self.add_field(0, "Name on the report", self.ent_name)
        self.add_field(1, "Systolic threshold mmHg",
                       tools.get_entry(self.frm_fields, self.systolic,
                                       "integer"))
        self.add_field(2, "Diastolic threshold mmHg",
                       tools.get_entry(self.frm_fields, self.diastolic,
                                       "integer"))
        self.add_field(3, "Days shown at start",
                       tools.get_entry(self.frm_fields, self.period_days,
                                       "integer"))
        ttk.Label(self.frm_fields, style="App.TLabel", justify=tk.LEFT,
                  text="A reading is marked when either value reaches its"
                       " threshold.\nAt home the ESH 2021 threshold is"
                       " 135/85: change it if your doctor says so.").grid(
                           row=4, column=0, columnspan=2, sticky=tk.W,
                           pady=(8, 0))

        buttons = tools.get_button_column(frm_main,
                                          (("Save", self.on_save),
                                           ("Close", self.on_cancel)),
                                          window=self)
        self.frm_fields.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        buttons.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        frm_main.pack(fill=tk.BOTH, expand=1)

    def add_field(self, row, caption, widget):
        ttk.Label(self.frm_fields, text=caption,
                  style="App.TLabel").grid(row=row, column=0, sticky=tk.W)
        widget.grid(row=row, column=1, sticky=tk.W, padx=5, pady=4)

    def on_open(self):
        """Fill the form and show it; called by the register of windows."""
        self.title("Settings")
        self.patient_name.set(self.engine.get_setting("patient_name"))
        self.systolic.set(self.engine.get_setting("systolic_threshold_mmhg"))
        self.diastolic.set(
            self.engine.get_setting("diastolic_threshold_mmhg"))
        self.period_days.set(self.engine.get_setting("period_days"))
        self.engine.tools.center_me(self, self.master)
        self.ent_name.focus_set()

    def get_problem(self):
        """What is wrong with the form, in words, or None."""
        days = self.period_days.get().strip()
        problem = None
        try:
            Threshold(self.systolic.get(), self.diastolic.get())
        except ValueError:
            problem = ("The thresholds are two whole numbers of mmHg, the"
                       " systolic higher than the diastolic.")
        if problem is None and not days.isdecimal():
            problem = "The days shown at start are a whole number."
        elif problem is None and not 0 < int(days) <= MAX_PERIOD_DAYS:
            problem = "The days shown at start go from 1 to {0}.".format(
                MAX_PERIOD_DAYS)
        return problem

    def on_save(self, evt=None):
        problem = self.get_problem()
        if problem is None:
            self.set_saved()
        else:
            messagebox.showwarning(APP_NAME, problem, parent=self)
        return "break"

    def set_saved(self):
        tools = self.engine.tools
        self.engine.set_settings({
            "patient_name": tools.get_clean_text(self.patient_name.get()),
            "systolic_threshold_mmhg": str(int(self.systolic.get())),
            "diastolic_threshold_mmhg": str(int(self.diastolic.get())),
            "period_days": str(int(self.period_days.get()))})
        # Closed first: notify is synchronous.
        self.on_cancel()
        self.engine.events.notify("settings", None)

    def on_cancel(self, evt=None):
        self.destroy()
