# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The entry strip: where a reading is typed, every day.

Three numbers and Enter. The numbers come first because they are what
changes; the position stays as it was last time, and the date and time
follow the clock.

They follow it for as long as nobody touches them. A window left open from
the morning would otherwise stamp an evening reading with the morning's
time, and that is a wrong datum nobody would notice. The strip remembers
what it last wrote in the two fields: when they no longer say that, a person
has changed them, and the clock lets go until the reading is saved.

A correction (R6) comes through the same strip: set_correction fills it
with a reading, and saving disables that one and stores the new one in a
single transaction. Escape gives up the correction.

The strip tells nobody directly. It saves and notifies "readings"; who
listens is not its business.
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


class EntryStrip(ttk.Frame):
    """Systolic, diastolic, heart rate, position, date and time; Enter."""

    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame", padding=(8, 8, 8, 4))
        self.engine = self.nametowidget(".").engine

        self.systolic = tk.StringVar()
        self.diastolic = tk.StringVar()
        self.heart_rate = tk.StringVar()
        self.position_id = tk.IntVar()
        self.time = tk.StringVar()
        self.message = tk.StringVar()

        # The reading being corrected, or None for a new one.
        self.correcting = None
        # What the strip last wrote in date and time, to tell a person's
        # change from its own.
        self.shown_date = None
        self.shown_time = None
        self.tick = None

        self.init_ui()
        self.set_keys()
        self.set_now()
        self.tick = self.after(TICK_MS, self.on_tick)

    def init_ui(self):
        tools = self.engine.tools
        fields = ttk.Frame(self, style="App.TFrame")

        self.ent_systolic = self.add_number(fields, "Systolic mmHg",
                                            self.systolic)
        self.ent_diastolic = self.add_number(fields, "Diastolic mmHg",
                                             self.diastolic)
        self.ent_heart_rate = self.add_number(fields, "Heart rate bpm",
                                              self.heart_rate)

        frm_position = ttk.LabelFrame(fields, text="Position",
                                      style="App.TLabelframe")
        positions = self.engine.get_positions()
        for row in positions:
            ttk.Radiobutton(frm_position, text=row["description"],
                            value=row["position_id"],
                            variable=self.position_id,
                            style="App.TRadiobutton").pack(side=tk.LEFT,
                                                           padx=4, pady=2)
        self.position_id.set(positions[0]["position_id"])
        frm_position.pack(side=tk.LEFT, padx=4, fill=tk.Y)

        self.date = Calendarium(fields, "Date")
        self.date.pack(side=tk.LEFT, padx=4)

        frm_time = ttk.LabelFrame(fields, text="Time",
                                  style="App.TLabelframe")
        self.ent_time = ttk.Entry(frm_time, textvariable=self.time, width=9,
                                  justify=tk.CENTER)
        self.ent_time.pack(padx=4, pady=4)
        frm_time.pack(side=tk.LEFT, padx=4, fill=tk.Y)

        self.btn_save = ttk.Button(fields, text="Save", style="App.TButton",
                                   width=tools.BUTTON_WIDTH,
                                   command=self.on_save)
        self.btn_save.pack(side=tk.LEFT, padx=8)

        fields.pack(side=tk.TOP, anchor=tk.W)
        ttk.Label(self, textvariable=self.message,
                  style="App.TLabel").pack(side=tk.TOP, anchor=tk.W, padx=4)

    def add_number(self, container, caption, variable):
        frame = ttk.LabelFrame(container, text=caption,
                               style="App.TLabelframe")
        entry = self.engine.tools.get_entry(frame, variable, "integer")
        entry.pack(padx=4, pady=4)
        frame.pack(side=tk.LEFT, padx=4, fill=tk.Y)
        return entry

    def set_keys(self):
        """Enter saves and Escape gives up, from any field of the strip."""
        for widget in self.engine.tools.get_widgets(self):
            widget.bind("<Return>", self.on_save)
            widget.bind("<KP_Enter>", self.on_save)
            widget.bind("<Escape>", self.on_cancel)

    # --- the clock -----------------------------------------------------------

    def set_now(self):
        now = datetime.datetime.now().replace(microsecond=0)
        if self.date.get_date() != now.date():
            self.date.set_date(now.date())
        self.time.set(now.strftime("%H:%M:%S"))
        self.shown_date = now.date()
        self.shown_time = self.time.get()

    def is_untouched(self):
        """Whether date and time still say what the strip wrote in them."""
        return (self.correcting is None
                and self.date.get_date() == self.shown_date
                and self.time.get() == self.shown_time)

    def on_tick(self):
        if self.is_untouched():
            self.set_now()
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
        """What is wrong with the strip, in words, or None."""
        moment = self.get_moment()
        numbers = self.get_numbers()
        problem = None
        if numbers is None:
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
                                  self.correcting):
            problem = ("There is already a reading at that second."
                       " Correct it from the list instead.")
        return problem

    # --- saving --------------------------------------------------------------

    def on_save(self, evt=None):
        problem = self.get_problem()
        if problem is None:
            self.set_saved()
        else:
            messagebox.showwarning(APP_NAME, problem,
                                   parent=self.winfo_toplevel())
            self.ent_systolic.focus_set()
        return "break"

    def set_saved(self):
        moment = self.get_moment()
        stored = self.engine.get_stored(moment)
        systolic, diastolic, heart_rate = self.get_numbers()
        values = self.engine.get_reading_values(stored,
                                                self.position_id.get(),
                                                systolic, diastolic,
                                                heart_rate)
        if self.correcting is None:
            reading_id = self.engine.add_reading(values)
            verb = "Saved"
        else:
            reading_id = self.engine.correct_reading(self.correcting, values)
            verb = "Corrected"

        self.set_clear()
        self.message.set("{0}: {1}/{2} mmHg, {3} bpm at {4}.".format(
            verb, systolic, diastolic, heart_rate,
            self.engine.get_shown_moment(moment)))
        # Last: notify is synchronous, and the strip is already clear.
        self.engine.events.notify("readings", reading_id)

    # --- correcting ----------------------------------------------------------

    def set_correction(self, reading_id):
        """Fill the strip with a reading, to be saved as its correction."""
        row = self.engine.get_reading(reading_id)
        moment = self.engine.get_moment(row["recorded_at"])
        self.correcting = reading_id
        self.systolic.set(str(row["systolic_mmhg"]))
        self.diastolic.set(str(row["diastolic_mmhg"]))
        self.heart_rate.set(str(row["heart_rate_bpm"]))
        self.position_id.set(row["position_id"])
        self.date.set_date(moment.date())
        self.time.set(moment.strftime("%H:%M:%S"))
        self.message.set("Correcting the reading of {0}. Enter saves the"
                         " correction, Escape gives it up.".format(
                             self.engine.get_shown_moment(moment)))
        self.ent_systolic.focus_set()
        self.ent_systolic.select_range(0, tk.END)

    def on_cancel(self, evt=None):
        if self.correcting is not None:
            self.set_clear()
            self.message.set("Correction given up.")
        return "break"

    def set_clear(self):
        """Ready for the next reading: empty numbers, the clock back on."""
        self.correcting = None
        for variable in (self.systolic, self.diastolic, self.heart_rate):
            variable.set("")
        self.set_now()
        self.message.set("")
        self.ent_systolic.focus_set()
