# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""How to measure: a text to read, from docs/how_to_measure.txt.

The text lives in a file and not in the code, so it is corrected without
touching the program, and read on GitHub as it is read here. Shown read
only; one window at a time, through the register of windows with show.
"""

import os
import tkinter as tk
from tkinter import ttk

from version import APP_NAME

# The text, beside the program.
GUIDE = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "docs", "how_to_measure.txt")


class Guide(tk.Toplevel):
    """The text, and nothing to press: Escape or the X closes it."""

    def __init__(self, parent):
        super().__init__(parent, name="guide")
        self.engine = self.nametowidget(".").engine
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.engine.tools.hide_me(self)
        frame = ttk.Frame(self, style="App.TFrame", padding=8)
        self.text = self.engine.tools.get_text(frame)
        self.text.configure(width=80, height=34, font="TkFixedFont")
        frame.pack(fill=tk.BOTH, expand=1)
        self.bind("<Escape>", self.on_cancel)

    def on_open(self):
        """Read the file and show it; called by the register of windows."""
        self.title("{0} - how to measure".format(APP_NAME))
        with open(GUIDE, "r", encoding="utf-8") as f:
            self.engine.tools.set_text(self.text, f.read())
        self.engine.tools.center_me(self, self.master)
        self.text.focus_set()

    def on_cancel(self, evt=None):
        self.destroy()
