#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Build a sample diary of invented readings in a new file.

    python3 seed.py sample.sl3
    python3 sphygmus.py --database sample.sl3

The same readings the demo diary has (File > Demo diary), in a file that
stays: to look at with sqlite3, to take the pictures from, to try the
program on outside it. See sample.py.

The file must not exist. This script never opens a diary somebody keeps.
"""

import os
import sys

from engine import Engine
from log import Log
from sample import Sample

USAGE = "usage: python3 seed.py NEW_FILE.sl3"


def main():
    if len(sys.argv) != 2:
        raise SystemExit(USAGE)
    path = os.path.abspath(sys.argv[1])
    if os.path.exists(path):
        raise SystemExit("{0} exists: the seed only writes a new file.\n{1}"
                         .format(path, USAGE))
    engine = Engine(path, Log(os.devnull))
    sittings = Sample(engine).run()
    print("{0}: {1} sittings, {2} readings".format(
        path, sittings, engine.get_reading_count()))
    engine.db.close()


if __name__ == "__main__":
    main()
