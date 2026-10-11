# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the PDF report, on the invented readings of sample.py.

Skipped where ReportLab is not installed, which is the program's own rule:
the report is optional. What the PDF looks like is checked by rendering it
(pdftoppm), by a person; these check that it is written and whole.
"""

import datetime
import os
import shutil
import tempfile
import unittest

from engine import Engine
from log import Log
from report import HAS_REPORTLAB, Report
from sample import Sample


@unittest.skipUnless(HAS_REPORTLAB, "no ReportLab")
class ReportTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.path = os.path.join(self.folder, "report.pdf")
        self.engine = Engine(":memory:", Log(os.devnull))
        self.today = datetime.date.today()

    def tearDown(self):
        self.engine.db.close()
        shutil.rmtree(self.folder)

    def read(self):
        with open(self.path, "rb") as f:
            return f.read()

    def test_report_of_a_month_is_a_whole_pdf(self):
        Sample(self.engine).run()
        Report(self.engine).write(
            self.path, (self.today - datetime.timedelta(days=30), self.today))
        data = self.read()
        self.assertTrue(data.startswith(b"%PDF"))
        self.assertIn(b"%%EOF", data[-1024:])

    def test_long_period_runs_to_more_than_one_page(self):
        Sample(self.engine).run()
        Report(self.engine).write(
            self.path, (self.today - datetime.timedelta(days=60), self.today))
        self.assertGreater(self.read().count(b"/Type /Page\n"), 1)

    def test_empty_period_still_writes_a_report(self):
        Report(self.engine).write(self.path, (self.today, self.today))
        self.assertTrue(self.read().startswith(b"%PDF"))

    def test_name_with_markup_characters_is_written(self):
        self.engine.set_settings({"patient_name": "A & B <sample>"})
        Report(self.engine).write(self.path, (self.today, self.today))
        self.assertTrue(self.read().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
