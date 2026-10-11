# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The configuration file, an .ini read by hand.

The standard library has `configparser`, which does this and much more:
defaults, interpolation, values on several lines, writing back. This class
only reads, so that a reader can see what reading an .ini file means: go
through it line by line and decide, for each line, what it is.

    ; a comment, and so is a line starting with #
    [database]
    path = sphygmus.sl3

It holds where things are, and nothing about the readings: the threshold is
a row in the diary, so it travels with the diary.
"""

import os


class Config:
    """Sections of key = value pairs, read once from an .ini file."""

    def __init__(self, path):
        self.path = path
        # section -> {key: value}, the settings as text
        self.sections = {}
        self.read()

    def read(self):
        """Read the file line by line into self.sections.

        Anything that is not a blank line, a comment, a [section] or a
        key = value inside a section is refused, naming the line: a typo in
        the file stops the program here rather than somewhere else.
        """
        section = None

        with open(self.path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for number, line in enumerate(lines, start=1):
            text = line.strip()

            if text == "" or text[0] in (";", "#"):
                pass
            elif text.startswith("[") and text.endswith("]"):
                section = text[1:-1].strip()
                if section in self.sections:
                    raise self.get_error(number,
                                         "section [{0}] twice".format(section))
                self.sections[section] = {}
            elif section is None:
                raise self.get_error(number,
                                     "outside any section: {0}".format(text))
            elif "=" not in text:
                raise self.get_error(number, 'no "=" in "{0}"'.format(text))
            else:
                self.set_pair(number, section, text)

    def set_pair(self, number, section, text):
        # On the first "=" only, so a value may contain one.
        key, value = text.split("=", 1)
        key = key.strip()
        if key == "":
            raise self.get_error(number, 'no key before "="')
        if key in self.sections[section]:
            raise self.get_error(number,
                                 "{0} twice in [{1}]".format(key, section))
        self.sections[section][key] = value.strip()

    def get_error(self, number, message):
        """A ValueError that says which file and which line."""
        return ValueError("{0}, line {1}: {2}".format(
            os.path.basename(self.path), number, message))

    def get(self, section, key):
        """The value of a key, as text."""
        name = os.path.basename(self.path)
        if section not in self.sections:
            raise ValueError("{0}: no section [{1}]".format(name, section))
        if key not in self.sections[section]:
            raise ValueError("{0}: no {1} in [{2}]".format(name, key,
                                                           section))
        return self.sections[section][key]
