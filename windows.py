# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The Singleton pattern, one window per name, written by hand.

A textbook Singleton is a class that allows a single instance of itself.
What an application needs is one open window per name: one form for a
reading, one settings window. So this is a register of the open windows,
by name - a pattern also called Multiton.

Two rules:

    show(name, build)     settings, How to measure: if it is already open,
                          bring it to the front; build it only if it is not.
    replace(name, build)  the form of a reading, which is about one row: the
                          one open is closed through its own on_cancel, and
                          a new one is built. A double click on another row
                          therefore moves the form, it does not add one.

build is a function that makes the window, not a window: when the answer is
"it is already open", nothing is built at all.

Taken from Biovarase.
"""


class Windows:
    """The windows open now, by name."""

    def __init__(self, log):
        # The log, for the trace (--trace).
        self.log = log
        # name -> the window open under that name.
        self.dict_instances = {}

    def get(self, name):
        """The window open under this name, or None."""
        return self.dict_instances.get(name)

    def show(self, name, build):
        """The window called name: the one open, brought forward, or new."""
        window = self.dict_instances.get(name)
        if window is None:
            window = self.add(name, build)
        else:
            window.lift()
            window.focus_set()
            self.log.trace("{0}: already open, brought forward".format(name))
        return window

    def replace(self, name, build):
        """A new window called name, after closing the one open under it."""
        window = self.dict_instances.get(name)
        if window is not None:
            self.log.trace("{0}: closing the one open".format(name))
            window.on_cancel()
        return self.add(name, build)

    def add(self, name, build):
        """Build the window, remember it, open it; forget it when it goes.

        <Destroy> arrives however the window is closed - a button, the
        title bar's X, the application ending - so the register cannot be
        left holding a window that is gone.
        """
        window = build()
        self.dict_instances[name] = window
        window.bind("<Destroy>",
                    lambda evt: self.forget(name, window, evt), add="+")
        window.on_open()
        self.log.trace("{0}: built; open = {1}".format(
            name, list(self.dict_instances)))
        return window

    def forget(self, name, window, evt):
        """Take a destroyed window out of the register.

        A Toplevel receives <Destroy> for every widget inside it as well:
        only its own counts. And only while it is still the window
        registered under that name, not one that has already been replaced.
        """
        if (str(evt.widget) == str(window)
                and self.dict_instances.get(name) is window):
            del self.dict_instances[name]
            self.log.trace("{0}: forgotten; open = {1}".format(
                name, list(self.dict_instances)))
