# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The application: the root window, and the engine it owns.

App inherits from tk.Tk because it *is* the root window. What it needs from
outside - where the diary is, the log, the theme - it declares by name in
its signature, and main() hands it over: App reads no file and no argument
itself. tk.Tk gets only what belongs to tk.Tk, className, by name.
"""

import tkinter as tk
from tkinter import messagebox

from engine import Engine
from ui.icon import ICONS
from ui.main import Main
from version import APP_NAME


class App(tk.Tk):
    """The root window, holding the one Engine."""

    def __init__(self, database, log, theme):
        # First, before anything that needs Tk: until tk.Tk.__init__ has
        # run there is no interpreter behind self, and self.title() would
        # look for one forever.
        super().__init__(className="sphygmus")
        # Built hidden and shown in place: otherwise the window appears
        # empty in a corner, fills in, and jumps.
        self.withdraw()

        self.engine = Engine(database, log)

        self.title(APP_NAME)
        self.set_icon()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.engine.tools.set_style(theme)

        self.main = Main(self)
        self.main.pack(fill=tk.BOTH, expand=1)

        # The root has no parent, so center_me places it on the screen: in
        # the middle across, a third of the way down.
        self.engine.tools.center_me(self)
        # The keyboard on the list, on its first row: arrows move, Enter
        # opens, Alt+N starts a new reading.
        self.main.readings.set_first()
        self.engine.log.trace("ready")

    def set_icon(self):
        """The icon, in every size the window manager may ask for.

        The images are kept on the instance: Tk holds them by name, and a
        PhotoImage nobody keeps is collected, leaving an empty icon.
        True: every window opened later carries it too. master=self, or
        the image belongs to whichever Tk was created first in the process.
        """
        self.icons = [tk.PhotoImage(master=self, data=data)
                      for data in ICONS]
        self.iconphoto(True, *self.icons)

    def report_callback_exception(self, exc, val, tb):
        """Tkinter calls this for an exception raised in a callback.

        A button, a menu, an after(): every error coming out of the
        interface ends up here, the one net. It is written to the log with
        its traceback and shown, so nothing fails in silence.
        """
        self.engine.log.exception("{0}: {1}".format(exc.__name__, val))
        messagebox.showerror(APP_NAME,
                             "{0}\n\n{1}".format(val, self.engine.log.path),
                             parent=self.get_active_window())

    def get_active_window(self):
        """The window on top, to hang a box on.

        A box whose parent is the root opens behind a dialog transient of
        it, and the program looks as though it had stopped.
        """
        window = self
        widget = self.focus_displayof()
        if widget is not None:
            window = widget.winfo_toplevel()
        return window

    def on_exit(self, evt=None):
        """Close the diary and go.

        No question first: nothing is left unsaved, because a reading is
        saved when it is entered.
        """
        self.engine.db.close()
        self.engine.log.trace("diary closed")
        self.destroy()
