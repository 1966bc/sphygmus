# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The readings drawn by hand on a tk.Canvas, no plotting library.

Each reading is a vertical line from its diastolic to its systolic, a dot
at each end: filled when seated, hollow when lying down, so the two
positions are told apart without a second chart (R5). The thresholds are
two dashed lines (R4). Time runs across, placed by the moment and not by
rank, so a week with no reading shows as the gap it was.

It is handed numbers and draws them; it does not know the diary exists.
The axes come from the domain, pressure.scale and pressure.timeline, which
the PDF asks too: the two charts cannot draw the same readings two ways.
"""

import tkinter as tk

from pressure.scale import Scale
from pressure.timeline import Timeline

# Room around the plot, in pixels: the numbers of the axis on the left, the
# days below, the legend above.
MARGIN_LEFT = 52
MARGIN_RIGHT = 24
MARGIN_TOP = 34
MARGIN_BOTTOM = 38

# Colours by meaning. Systolic and diastolic told apart by hue and by
# position on the line; the threshold in the colour that marks a reading
# over it in the list.
SYSTOLIC = "#33679e"
DIASTOLIC = "#3a9a5a"
SPAN = "#a9a9a5"
THRESHOLD = "#ff0000"
GRID = "#dededa"
AXIS = "#000000"
PLOT = "#ffffff"

# Half the side of a dot, in pixels.
DOT = 3

SEATED = 1


class PressureCanvas(tk.Canvas):
    """Systolic and diastolic over a period, with the threshold."""

    def __init__(self, parent):
        super().__init__(parent, background=PLOT, highlightthickness=0,
                         width=900, height=420)
        self.readings = []
        self.threshold = None
        self.period = None
        self.bind("<Configure>", self.on_resize)

    def set_data(self, readings, threshold, period):
        """What to draw: (moment, position_id, systolic, diastolic) tuples,
        the Threshold, and (first day, last day) or None."""
        self.readings = readings
        self.threshold = threshold
        self.period = period
        self.set_drawing()

    def on_resize(self, evt=None):
        self.set_drawing()

    def set_drawing(self):
        self.delete(tk.ALL)
        if self.period is None or not self.readings:
            self.create_text(self.winfo_width() / 2,
                             self.winfo_height() / 2,
                             text="No readings in the period.", tags="empty")
        else:
            self.set_plot()

    def set_plot(self):
        systolic = [row[2] for row in self.readings]
        diastolic = [row[3] for row in self.readings]
        scale = Scale(min(diastolic + [self.threshold.diastolic_mmhg]),
                      max(systolic + [self.threshold.systolic_mmhg]))
        timeline = Timeline(*self.period)
        self.set_axes(scale, timeline)
        for value in (self.threshold.systolic_mmhg,
                      self.threshold.diastolic_mmhg):
            y = self.get_y(scale, value)
            self.create_line(MARGIN_LEFT, y, self.get_right(), y,
                             fill=THRESHOLD, dash=(6, 4), tags="threshold")
            self.create_text(self.get_right() - 2, y - 2, text=str(value),
                             fill=THRESHOLD, anchor=tk.SE)
        for moment, position_id, high, low in self.readings:
            x = self.get_x(timeline, moment)
            self.create_line(x, self.get_y(scale, low), x,
                             self.get_y(scale, high), fill=SPAN,
                             tags="span")
            self.set_dot(x, self.get_y(scale, high), SYSTOLIC, position_id,
                         "systolic")
            self.set_dot(x, self.get_y(scale, low), DIASTOLIC, position_id,
                         "diastolic")
        self.set_legend()

    def set_axes(self, scale, timeline):
        bottom = self.get_bottom()
        for value in scale.get_ticks():
            y = self.get_y(scale, value)
            self.create_line(MARGIN_LEFT, y, self.get_right(), y, fill=GRID)
            self.create_text(MARGIN_LEFT - 6, y, text=str(value),
                             anchor=tk.E)
        for day in timeline.get_ticks():
            x = self.get_day_x(timeline, day)
            self.create_line(x, bottom, x, bottom + 4, fill=AXIS)
            self.create_text(x, bottom + 6, text=day.strftime("%d/%m"),
                             anchor=tk.N)
        self.create_rectangle(MARGIN_LEFT, MARGIN_TOP, self.get_right(),
                              bottom, outline=AXIS)
        self.create_text(MARGIN_LEFT - 6, MARGIN_TOP - 8, text="mmHg",
                         anchor=tk.SE)

    def set_dot(self, x, y, colour, position_id, tag):
        fill = colour
        if position_id != SEATED:
            fill = PLOT
        self.create_oval(x - DOT, y - DOT, x + DOT, y + DOT, outline=colour,
                         fill=fill, width=2, tags=tag)

    def set_legend(self):
        x = MARGIN_LEFT
        y = MARGIN_TOP / 2
        for caption, colour, position_id in (("systolic", SYSTOLIC, SEATED),
                                             ("diastolic", DIASTOLIC,
                                              SEATED)):
            self.set_dot(x + DOT, y, colour, position_id, "legend")
            x = self.get_text_end(x + 3 * DOT, y, caption) + 16
        self.set_dot(x + DOT, y, AXIS, SEATED, "legend")
        x = self.get_text_end(x + 3 * DOT, y, "seated") + 12
        self.set_dot(x + DOT, y, AXIS, 0, "legend")
        self.get_text_end(x + 3 * DOT, y, "lying")
        self.create_text(self.get_right(), y, anchor=tk.E, fill=THRESHOLD,
                         text="- - threshold {0}".format(
                             self.threshold.get_caption()))

    def get_text_end(self, x, y, text):
        """Write text from x; return where it ends."""
        item = self.create_text(x, y, text=text, anchor=tk.W)
        return self.bbox(item)[2]

    # --- from values to pixels -----------------------------------------------

    def get_right(self):
        return max(MARGIN_LEFT + 1, self.winfo_width() - MARGIN_RIGHT)

    def get_bottom(self):
        return max(MARGIN_TOP + 1, self.winfo_height() - MARGIN_BOTTOM)

    def get_y(self, scale, value):
        """Upwards: the larger the value, the higher on the canvas."""
        height = self.get_bottom() - MARGIN_TOP
        return self.get_bottom() - scale.calc_fraction(value) * height

    def get_x(self, timeline, moment):
        width = self.get_right() - MARGIN_LEFT
        return MARGIN_LEFT + timeline.calc_fraction(moment) * width

    def get_day_x(self, timeline, day):
        """A day is placed at its first instant."""
        return self.get_x(timeline, timeline.first + (day - timeline.start))
