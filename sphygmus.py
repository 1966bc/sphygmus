#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Start sphygmus.

    python3 sphygmus.py                        start it
    python3 sphygmus.py --trace                and print what it does
    python3 sphygmus.py --database sample.sl3  on another diary

--database opens a diary that is not the one sphygmus.ini names - the
sample built by seed.py, a backup to look into - without editing the ini:
an ini pointed elsewhere for one afternoon is an ini still pointed there a
week later. The file must exist: a mistyped name must not start an empty
diary nobody asked for.

main() is the one place that reads the outside world: the options on the
command line and sphygmus.ini. What it reads it hands to App by name, so a
misspelt parameter is a TypeError at the call, before any window opens.
"""

import os
import sys
from tkinter import messagebox

from config import Config
from log import Log
from ui.app import App
from version import APP_NAME

# The folder of this file: the ini, the log and by default the diary live
# here, so the program can be started from any folder.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# The options the program knows are --trace and --database PATH. Anything
# else is refused, not ignored.
USAGE = "usage: python3 sphygmus.py [--trace] [--database PATH]"


def main():

    # sys.argv[0] is the program, the rest is ours, read by hand.
    options = sys.argv[1:]
    tracing = False
    chosen = None
    unknown = []
    index = 0
    while index < len(options):
        option = options[index]
        if option == "--trace":
            tracing = True
        elif option == "--database" and index + 1 < len(options):
            index += 1
            chosen = os.path.abspath(options[index])
        else:
            unknown.append(option)
        index += 1
    if unknown:
        raise SystemExit("unknown option: {0}\n{1}".format(" ".join(unknown),
                                                           USAGE))
    if chosen is not None and not os.path.isfile(chosen):
        raise SystemExit("no such diary: {0}".format(chosen))

    # The log comes first, so that even a failure to start is written down.
    log = Log(os.path.join(PROJECT_DIR, "sphygmus.log"), tracing)
    log.trace("options = {0}".format(options))

    # Before the main loop there is no report_callback_exception yet: a
    # failure here is written to the log, shown, and raised again.
    try:
        config = Config(os.path.join(PROJECT_DIR, "sphygmus.ini"))
        # os.path.join keeps an absolute path as it is.
        database = os.path.join(PROJECT_DIR, config.get("database", "path"))
        if chosen is not None:
            database = chosen
        app = App(database=database, log=log,
                  theme=config.get("window", "theme"))
    except Exception as exc:
        log.exception("start failed: {0}".format(exc))
        messagebox.showerror(APP_NAME, "{0}\n\n{1}".format(exc, log.path))
        raise

    app.mainloop()


if __name__ == "__main__":
    main()
