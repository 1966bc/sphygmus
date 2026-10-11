# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the invented readings of the demo and of seed.py."""

import datetime
import os
import unittest

from engine import Engine
from log import Log
from sample import DAYS, Sample


class SampleTestCase(unittest.TestCase):

    def get_readings(self):
        engine = Engine(":memory:", Log(os.devnull))
        Sample(engine).run()
        today = datetime.date.today()
        rows = engine.get_readings(today - datetime.timedelta(days=DAYS),
                                   today)
        engine.db.close()
        return [tuple(row) for row in rows]

    def test_same_readings_every_time(self):
        self.assertEqual(self.get_readings(), self.get_readings())

    def test_a_high_first_reading_has_two_more_a_minute_apart(self):
        moments = sorted(datetime.datetime.strptime(row[1],
                                                    "%Y-%m-%d %H:%M:%S")
                         for row in self.get_readings())
        minute = datetime.timedelta(minutes=1)
        triples = [moment for moment in moments
                   if moment + minute in moments
                   and moment + 2 * minute in moments]
        self.assertGreater(len(triples), 0)


if __name__ == "__main__":
    unittest.main()
