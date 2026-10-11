# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""Invented readings, for the demo diary and for seed.py.

A generator with a fixed seed, so the same diary comes out every time (R7:
no real reading in the repository, the pictures in the README included).
The readings imitate a real diary: morning and evening, mostly seated, now
and then lying down in the evening, and now and then a first reading that
is high, followed by two more a minute apart.

It is handed an engine and writes through it, as a typed reading is
written; it imports nothing of the program.
"""

import datetime
import random

# The same diary every time.
SEED = 1966

# Days of readings, ending today.
DAYS = 60

SEATED = 1
LYING = 2


class Sample:
    """Fill an empty diary with invented readings."""

    def __init__(self, engine):
        self.engine = engine
        self.random = random.Random(SEED)

    def get_values(self):
        """A plausible reading: systolic, diastolic, heart rate."""
        systolic = round(self.random.gauss(129, 8))
        diastolic = round(self.random.gauss(81, 6))
        heart_rate = round(self.random.gauss(67, 6))
        # The device never shows a diastolic at or above the systolic.
        diastolic = min(diastolic, systolic - 25)
        return (systolic, diastolic, heart_rate)

    def get_moment(self, day, hour, spread):
        minutes = self.random.randint(0, spread)
        return datetime.datetime.combine(
            day, datetime.time(hour)) + datetime.timedelta(minutes=minutes)

    def add(self, moment, position, values):
        systolic, diastolic, heart_rate = values
        self.engine.add_reading(self.engine.get_reading_values(
            self.engine.get_stored(moment), position, systolic, diastolic,
            heart_rate))

    def add_sitting(self, moment, position):
        """One reading, or three when the first is high.

        The second and the third a minute apart, and a little lower: the
        first reading is often the highest of a sitting.
        """
        first = self.get_values()
        self.add(moment, position, first)
        if first[0] >= 140 or first[1] >= 90:
            for minute in (1, 2):
                systolic, diastolic, heart_rate = self.get_values()
                self.add(moment + datetime.timedelta(minutes=minute),
                         position,
                         (min(systolic, first[0] - 4),
                          min(diastolic, first[1] - 2), heart_rate))

    def run(self):
        """Write the readings; return how many sittings."""
        today = datetime.date.today()
        now = datetime.datetime.now()
        count = 0
        for back in range(DAYS - 1, -1, -1):
            day = today - datetime.timedelta(days=back)
            # Now and then a morning is skipped, as in any real diary.
            if self.random.random() > 0.1:
                morning = self.get_moment(day, 7, 80)
                if morning < now:
                    self.add_sitting(morning, SEATED)
                    count += 1
            evening = self.get_moment(day, 20, 100)
            position = SEATED
            if self.random.random() < 0.3:
                position = LYING
            if evening < now:
                self.add_sitting(evening, position)
                count += 1
        self.engine.set_settings({"patient_name": "Sample diary"})
        return count
