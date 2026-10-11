# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The form of one reading: a new one, or one to correct.

Opened by the list - the plural opens the singular - through the register
of windows, with replace: there is one form at a time, and a double click
on another row closes the form open and opens it on that row. It is not
modal, so the list stays usable behind it.

A new reading has date and time following the clock for as long as nobody
touches them. A form left open from the morning would otherwise stamp an
evening reading with the morning's time, and that is a wrong datum nobody
would notice. The form remembers what it last wrote in the two fields:
when they no longer say that, a person has changed them, and the clock
lets go.

An existing reading opens with Enable ticked or not, as its column says
(R6). Unticking it takes the reading out of the diary; ticking a
removed one brings it back, if its second is still free. Changed values
are a correction: the reading is disabled and the new one stored in a
single transaction; unchanged values write nothing. Either way the form
closes and notifies "readings" with the id of the row saved, so the list
lands on it. Who listens is not the form's business.
"""

import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from ui.calendarium import Calendarium
from version import APP_NAME

# How often date and time are put back on the clock, in milliseconds, while
# nobody has touched them. A second, because the time shows seconds.
TICK_MS = 1000

# A reading more than this ahead of the clock is refused: it is a mistyped
# date, not a reading. A minute, for a clock a little behind the device's.
FUTURE_TOLERANCE = datetime.timedelta(minutes=1)


class Reading(tk.Toplevel):
    """Systolic, diastolic, heart rate, position, date and time."""

    def __init__(self, parent, reading_id=None):
        super().__init__(parent, name="reading")
        self.engine = self.nametowidget(".").engine
        # The reading being corrected, or None for a new one. Read from the
        # database when the form opens, never taken from the list's copy.
        self.reading_id = reading_id

        self.systolic = tk.StringVar()
        self.diastolic = tk.StringVar()
        self.heart_rate = tk.StringVar()
        self.position_id = tk.IntVar()
        self.time = tk.StringVar()
        # Ticked: the reading is in the diary, enable 1 (R6).
        self.enable = tk.BooleanVar(value=True)

        # What the form last wrote in date and time, to tell a person's
        # change from its own.
        self.shown_date = None
        self.shown_time = None
        self.tick = None

        self.transient(parent.winfo_toplevel())
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.engine.tools.hide_me(self)
        self.init_ui()
        self.set_keys()

    def init_ui(self):
        tools = self.engine.tools
        frm_main = ttk.Frame(self, style="App.TFrame", padding=8)
        self.frm_fields = ttk.Frame(frm_main, style="App.TFrame")

        self.ent_systolic = self.add_number(0, "Systolic mmHg",
                                            self.systolic)
        self.ent_diastolic = self.add_number(1, "Diastolic mmHg",
                                             self.diastolic)
        self.ent_heart_rate = self.add_number(2, "Heart rate bpm",
                                              self.heart_rate)

        frm_position = ttk.Frame(self.frm_fields, style="App.TFrame")
        for row in self.engine.get_positions():
            ttk.Radiobutton(frm_position, text=row["description"],
                            value=row["position_id"],
                            variable=self.position_id,
                            style="App.TRadiobutton").pack(side=tk.LEFT,
                                                           padx=(0, 8))
        self.add_field(3, "Position", frm_position)

        self.date = Calendarium(self.frm_fields)
        self.add_field(4, "Date", self.date)

        self.ent_time = ttk.Entry(self.frm_fields, textvariable=self.time,
                                  width=9, justify=tk.CENTER)
        self.add_field(5, "Time", self.ent_time)

        self.chk_enable = ttk.Checkbutton(self.frm_fields,
                                          variable=self.enable,
                                          style="App.TCheckbutton")
        self.add_field(6, "Enable", self.chk_enable)

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

    def add_number(self, row, caption, variable):
        entry = self.engine.tools.get_entry(self.frm_fields, variable,
                                            "integer")
        self.add_field(row, caption, entry)
        return entry

    def set_keys(self):
        """Enter saves and Escape closes, from any field of the form."""
        self.bind("<Return>", self.on_save)
        self.bind("<KP_Enter>", self.on_save)
        self.bind("<Escape>", self.on_cancel)

    def on_open(self):
        """Fill the form and show it; called by the register of windows."""
        if self.reading_id is None:
            self.title("New reading")
            # A reading is born in the diary: there is no removing what
            # has not been saved.
            self.chk_enable.state(("disabled",))
            self.position_id.set(self.engine.get_last_position_id())
            self.set_now()
            self.tick = self.after(TICK_MS, self.on_tick)
        else:
            self.set_values(self.engine.get_reading(self.reading_id))
        self.engine.tools.center_me(self, self.master)
        self.ent_systolic.focus_set()
        self.ent_systolic.select_range(0, tk.END)

    def set_values(self, row):
        moment = self.engine.get_moment(row["recorded_at"])
        title = "Reading of {0}".format(self.engine.get_shown_moment(moment))
        if not row["enable"]:
            title = "{0} - removed".format(title)
        self.title(title)
        self.enable.set(bool(row["enable"]))
        self.systolic.set(str(row["systolic_mmhg"]))
        self.diastolic.set(str(row["diastolic_mmhg"]))
        self.heart_rate.set(str(row["heart_rate_bpm"]))
        self.position_id.set(row["position_id"])
        self.date.set_date(moment.date())
        self.time.set(moment.strftime("%H:%M:%S"))

    # --- the clock -----------------------------------------------------------

    def set_now(self):
        now = datetime.datetime.now().replace(microsecond=0)
        if self.date.get_date() != now.date():
            self.date.set_date(now.date())
        self.time.set(now.strftime("%H:%M:%S"))
        self.shown_date = now.date()
        self.shown_time = self.time.get()

    def is_untouched(self):
        """Whether date and time still say what the form wrote in them."""
        return (self.date.get_date() == self.shown_date
                and self.time.get() == self.shown_time)

    def set_clock(self):
        """Put date and time back on the clock, unless a person moved them.
        """
        if self.is_untouched():
            self.set_now()

    def on_tick(self):
        # The only place a tick is scheduled, so destroy() always holds
        # the one pending and can cancel it.
        self.set_clock()
        self.tick = self.after(TICK_MS, self.on_tick)

    def destroy(self):
        if self.tick is not None:
            self.after_cancel(self.tick)
            self.tick = None
        super().destroy()

    # --- reading the fields --------------------------------------------------

    def get_time(self):
        """The time typed, with or without seconds, or None."""
        text = self.time.get().strip()
        found = None
        for pattern in ("%H:%M:%S", "%H:%M"):
            if found is None:
                try:
                    found = datetime.datetime.strptime(text, pattern).time()
                except ValueError:
                    found = None
        return found

    def get_moment(self):
        """Date and time together, or None when either is not one."""
        day = self.date.get_date()
        time = self.get_time()
        moment = None
        if day is not None and time is not None:
            moment = datetime.datetime.combine(day, time)
        return moment

    def get_numbers(self):
        """Systolic, diastolic, heart rate as integers, or None.

        None when any of the three is empty or is only a sign: the field
        lets "-" through while a number is being typed.
        """
        texts = [variable.get().strip()
                 for variable in (self.systolic, self.diastolic,
                                  self.heart_rate)]
        numbers = None
        if all(text.isdecimal() for text in texts):
            numbers = tuple(int(text) for text in texts)
        return numbers

    def get_problem(self):
        """What is wrong with the form, in words, or None.

        Nothing is asked of a reading being taken out of the diary: what it
        says no longer counts.
        """
        moment = self.get_moment()
        numbers = self.get_numbers()
        problem = None
        if not self.enable.get():
            problem = None
        elif numbers is None:
            problem = "Type systolic, diastolic and heart rate, all three."
        elif min(numbers) <= 0:
            problem = "A reading of zero is not a reading."
        elif numbers[0] <= numbers[1]:
            problem = "The systolic must be higher than the diastolic."
        elif moment is None:
            problem = ("That is not a date and a time. The time is"
                       " HH:MM:SS, or HH:MM.")
        elif moment > datetime.datetime.now() + FUTURE_TOLERANCE:
            problem = "That moment has not come yet."
        elif self.engine.is_taken(self.engine.get_stored(moment),
                                  self.reading_id):
            problem = ("There is already a reading at that second: if this"
                       " one was corrected, the correction holds it.")
        return problem

    def get_values(self):
        """The reading as the table wants it, keyed by column."""
        systolic, diastolic, heart_rate = self.get_numbers()
        return self.engine.get_reading_values(
            self.engine.get_stored(self.get_moment()),
            self.position_id.get(), systolic, diastolic, heart_rate)

    def is_unchanged(self, row, values):
        """Whether the form says what the reading already says.

        enable is left out: whether it is in the diary is the check box's
        question, asked apart.
        """
        return all(row[name] == value for name, value in values.items()
                   if name != "enable")

    # --- saving and closing --------------------------------------------------

    def on_save(self, evt=None):
        problem = self.get_problem()
        if problem is None:
            self.set_saved()
        else:
            messagebox.showwarning(APP_NAME, problem, parent=self)
            self.ent_systolic.focus_set()
        return "break"

    def set_saved(self):
        if self.reading_id is None:
            saved_id = self.engine.add_reading(self.get_values())
        else:
            saved_id = self.get_saved_id()
        self.engine.log.trace("saved {0}".format(saved_id))
        # Closed first: notify is synchronous, and the list it reaches
        # takes the focus.
        self.on_cancel()
        self.engine.events.notify("readings", saved_id)

    def get_saved_id(self):
        """Write what the form says about an existing reading; its id.

        Enable is the check box; the values are the fields.
        A change of values is a correction (R6): the reading is disabled,
        if it was not already, and a new one stored - which is also how a
        removed reading comes back corrected.
        """
        row = self.engine.get_reading(self.reading_id)
        saved_id = self.reading_id
        if not self.enable.get():
            if row["enable"]:
                self.engine.disable_reading(self.reading_id)
        else:
            values = self.get_values()
            if not self.is_unchanged(row, values):
                saved_id = self.engine.correct_reading(self.reading_id,
                                                       values)
            elif not row["enable"]:
                self.engine.enable_reading(self.reading_id)
        return saved_id

    def on_cancel(self, evt=None):
        self.destroy()
