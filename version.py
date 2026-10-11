# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The facts about the program, written once."""

APP_NAME = "Sphygmus"

__version__ = "0.1.0"
__date__ = "autumnus MMXXVI"
__author__ = "Giuseppe Costanzi (1966bc)"
__license__ = "GPL-3.0-or-later"

# The schema this program is written for: PRAGMA user_version of the diary.
# It changes with a numbered migration in sql/ddl, and a diary of another
# version is refused at startup rather than read wrong.
SCHEMA_VERSION = 1
