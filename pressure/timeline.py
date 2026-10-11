# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""A horizontal axis of days, from the first of a period to its last.

A reading is placed by the moment it was taken, not by its rank: three
readings a minute apart sit together, and a week with none shows as the
gap it was.
"""

import datetime
import math


class Timeline:
    """Days from start to end, both included."""

    def __init__(self, start, end):
        if start > end:
            raise ValueError("period starts {0}, after it ends {1}".format(
                start, end))
        self.start = start
        self.end = end
        # From the first instant of the first day to the first instant of
        # the day after the last, so a reading at 23:59 is still inside.
        self.first = datetime.datetime.combine(start, datetime.time())
        self.last = self.first + datetime.timedelta(
            days=(end - start).days + 1)

    def get_days(self):
        return (self.end - self.start).days + 1

    def calc_fraction(self, moment):
        """Where a moment falls, 0.0 at the start and 1.0 past the end."""
        span = (self.last - self.first).total_seconds()
        return (moment - self.first).total_seconds() / span

    def get_ticks(self, ticks=8):
        """The days to label: at most ticks of them, evenly spaced."""
        step = max(1, math.ceil(self.get_days() / ticks))
        days = []
        day = self.start
        while day <= self.end:
            days.append(day)
            day += datetime.timedelta(days=step)
        return days
