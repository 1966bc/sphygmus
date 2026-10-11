# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""A vertical axis with round numbers on it.

What a plotting library does before it draws anything: given the lowest and
the highest value, choose a step a person reads easily, start below the
lowest value and end above the highest on a multiple of that step.
"""

import math


class Scale:
    """A linear axis from lower to upper, ticked every step."""

    # The steps a person reads without effort, in mmHg or beats per minute.
    STEPS = (1, 2, 5, 10, 20, 25, 50, 100, 200, 500)

    def __init__(self, low, high, ticks=6):
        if low > high:
            raise ValueError("low {0} above high {1}".format(low, high))
        self.step = self.calc_step(high - low, ticks)
        self.lower = math.floor(low / self.step) * self.step
        self.upper = math.ceil(high / self.step) * self.step
        # One value only, or all equal: an axis still needs a height.
        if self.upper == self.lower:
            self.upper = self.lower + self.step

    def calc_step(self, span, ticks):
        """The smallest step that needs no more than ticks intervals."""
        found = self.STEPS[-1]
        for step in reversed(self.STEPS):
            if span / step <= ticks:
                found = step
        return found

    def get_ticks(self):
        values = []
        value = self.lower
        while value <= self.upper:
            values.append(value)
            value += self.step
        return values

    def calc_fraction(self, value):
        """Where a value falls, 0.0 at lower and 1.0 at upper."""
        return (value - self.lower) / (self.upper - self.lower)
