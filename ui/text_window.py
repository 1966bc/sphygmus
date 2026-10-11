# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""A text file, to be read: How to measure, the licence.

The texts live in files and not in the code, so they are corrected without
touching the program, and read on GitHub as they are read here. Shown read
only, in a fixed width font, because both are laid out in columns of plain
text. One window per text, through the register of windows with show.
"""

import os
import tkinter as tk
from tkinter import ttk

from version import APP_NAME

# The program's folder: the texts are paths below it.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GUIDE = os.path.join(ROOT, "docs", "how_to_measure.txt")
LICENCE = os.path.join(ROOT, "LICENSE")


class TextWindow(tk.Toplevel):
    """A text and nothing to press: Escape or the X closes it."""

    def __init__(self, parent, name, caption, path):
        super().__init__(parent, name=name)
        self.engine = self.nametowidget(".").engine
        self.caption = caption
        self.path = path
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.engine.tools.hide_me(self)
        frame = ttk.Frame(self, style="App.TFrame", padding=8)
        self.text = self.engine.tools.get_text(frame)
        self.text.configure(width=80, height=34, font="TkFixedFont")
        frame.pack(fill=tk.BOTH, expand=1)
        self.bind("<Escape>", self.on_cancel)

    def on_open(self):
        """Read the file and show it; called by the register of windows."""
        self.title("{0} - {1}".format(APP_NAME, self.caption))
        with open(self.path, "r", encoding="utf-8") as f:
            self.engine.tools.set_text(self.text, f.read())
        self.engine.tools.center_me(self, self.master)
        self.text.focus_set()

    def on_cancel(self, evt=None):
        self.destroy()
