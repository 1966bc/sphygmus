# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""A date widget: day, month and year in three spinboxes.

Derived from Calendarium 2.5 (github.com/1966bc/calendarium, MIT, same
author), and rewritten rather than copied for one reason: there the two
classes share their logic through a base class mixed into a tk and a ttk
frame, and this project has no mixins. Here there is one class, built from
ttk so it follows the theme, and the three spinboxes are attributes of it.

What it keeps from 2.5: a field refuses anything but digits as it is typed,
an impossible date such as 31 February is answered with None and never with
an exception, and a change of date, typed or set, is announced once as the
virtual event DATE_CHANGED.

It opens no dialog. The widget says whether the date is valid; what to tell
the user about it is the caller's business.
"""

import datetime
import tkinter as tk
from tkinter import ttk

# Generated when the date changes, by typing, by the arrows or by a set_
# method: whoever shows something that depends on the date binds to it.
DATE_CHANGED = "<<DateChanged>>"


class Calendarium(ttk.LabelFrame):
    """Day, month and year, read as one date or as None."""

    PARTS = ("day", "month", "year")

    # Characters per field. The year is as wide as datetime allows.
    WIDTHS = {"day": 3, "month": 3, "year": 5}

    RANGES = {"day": (1, 31), "month": (1, 12), "year": (1, 9999)}

    def __init__(self, parent, caption="",
                 labels=("Giorno", "Mese", "Anno")):
        super().__init__(parent, text=caption)

        self.labels = dict(zip(self.PARTS, labels))
        self.pending = None
        self.spins = {}

        today = datetime.date.today()
        self.day = tk.StringVar(self, value=str(today.day))
        self.month = tk.StringVar(self, value=str(today.month))
        self.year = tk.StringVar(self, value=str(today.year))

        self.init_ui()

        for variable in (self.day, self.month, self.year):
            variable.trace_add("write", self.on_write)

    # No __str__ here, and none on any widget class: Tk uses str(widget) as
    # the widget's path name, and parent=self would fail with 'bad window
    # path name'.

    def init_ui(self):
        check = (self.register(self.is_digits), "%d", "%S")
        for part in self.PARTS:
            frame = ttk.LabelFrame(self, text=self.labels[part])
            low, high = self.RANGES[part]
            spin = ttk.Spinbox(frame, width=self.WIDTHS[part], from_=low,
                               to=high, justify=tk.CENTER,
                               textvariable=getattr(self, part),
                               validate="key", validatecommand=check)
            spin.pack(padx=2, pady=2)
            frame.pack(side=tk.LEFT, padx=2)
            self.spins[part] = spin

    def is_digits(self, action, text):
        """Allow a keystroke only if what it inserts is digits.

        isdecimal and not isdigit: the superscript two answers yes to
        isdigit and then raises in int(). Deleting is always allowed, or a
        field could never be emptied to type it again.
        """
        allowed = action != "1" or text.isdecimal()
        return allowed

    # --- the event -----------------------------------------------------------

    def on_write(self, *args):
        # set_date writes three variables: one event for all three, when idle.
        if self.pending is None:
            self.pending = self.after_idle(self.on_changed)

    def on_changed(self):
        self.pending = None
        # Tk drops a virtual event aimed at a widget whose window does not
        # exist yet: a set_date while a form is being built would go
        # unannounced. winfo_id makes the window exist.
        self.winfo_id()
        self.event_generate(DATE_CHANGED)

    def destroy(self):
        if self.pending is not None:
            self.after_cancel(self.pending)
            self.pending = None
        super().destroy()

    # --- setting -------------------------------------------------------------

    def set_date(self, value):
        self.day.set(str(value.day))
        self.month.set(str(value.month))
        self.year.set(str(value.year))

    def set_today(self):
        self.set_date(datetime.date.today())

    def set_days_ago(self, days):
        self.set_date(datetime.date.today() - datetime.timedelta(days=days))

    def set_state(self, state):
        """tk.NORMAL or tk.DISABLED, for the three fields at once."""
        for spin in self.spins.values():
            spin.configure(state=state)

    def set_focus(self):
        """The keyboard on the day, where an impossible date usually is."""
        self.spins["day"].focus_set()

    # --- reading -------------------------------------------------------------

    def get_date(self):
        """The date, or None when the three fields do not make one.

        An empty field fails in int(), 31 February in date(): both are the
        same answer to the caller, not a date.
        """
        value = None
        try:
            value = datetime.date(int(self.year.get()),
                                  int(self.month.get()),
                                  int(self.day.get()))
        except ValueError:
            value = None
        return value

    def is_valid(self):
        return self.get_date() is not None

    def get_iso(self):
        """The date as ISO 8601 text, which is how dates are stored, or None.
        """
        value = self.get_date()
        iso = None
        if value is not None:
            iso = value.isoformat()
        return iso


def main():
    root = tk.Tk()
    root.title("Calendarium")

    frame = ttk.Frame(root, padding=8)
    start = Calendarium(frame, "Dal")
    end = Calendarium(frame, "Al")
    start.set_days_ago(30)
    start.pack(side=tk.LEFT, padx=4)
    end.pack(side=tk.LEFT, padx=4)
    frame.pack()

    shown = tk.StringVar(root)
    ttk.Label(root, textvariable=shown).pack(pady=(0, 8))

    def show(evt=None):
        shown.set("{0} - {1}".format(start.get_iso(), end.get_iso()))

    start.bind(DATE_CHANGED, show)
    end.bind(DATE_CHANGED, show)
    show()
    root.mainloop()


if __name__ == "__main__":
    main()
