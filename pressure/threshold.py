# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The threshold a reading is flagged against (R4)."""


class Threshold:
    """Systolic and diastolic limits, in mmHg.

    A reading is over when either value reaches its limit: >=, because
    that is how the guidelines write their thresholds (135/85 or more).
    Over is a flag, not a diagnosis, and it is never stored.
    """

    def __init__(self, systolic_mmhg, diastolic_mmhg):
        self.systolic_mmhg = self.check_limit(systolic_mmhg)
        self.diastolic_mmhg = self.check_limit(diastolic_mmhg)
        if self.systolic_mmhg <= self.diastolic_mmhg:
            raise ValueError("systolic threshold {0} is not above diastolic"
                             " {1}".format(systolic_mmhg, diastolic_mmhg))

    def check_limit(self, value):
        """A limit is a whole number of mmHg above zero, or it is refused.

        It arrives as text from the settings table, so a typo there stops
        here, saying what it was, instead of flagging nothing.
        """
        text = str(value).strip()
        if not text.isdecimal() or int(text) <= 0:
            raise ValueError("not a threshold in mmHg: {0!r}".format(value))
        return int(text)

    def is_over(self, systolic_mmhg, diastolic_mmhg):
        return (systolic_mmhg >= self.systolic_mmhg
                or diastolic_mmhg >= self.diastolic_mmhg)

    def get_caption(self):
        return "{0}/{1} mmHg".format(self.systolic_mmhg, self.diastolic_mmhg)
