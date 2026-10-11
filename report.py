# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The report to take to the doctor: a PDF, with ReportLab.

The heading, the statistics by position, the chart, then every reading of
the period in the order it was taken. Only the readings in the diary:
removed ones are not part of it (R6).

Written for a black and white printer: systolic and diastolic are told
apart by shape - a circle and a square - and not only by shade, seated and
lying down by filled and hollow, a reading over the threshold by bold type
and an asterisk. The chart asks the same domain as the screen,
pressure.scale and pressure.timeline, so the two cannot disagree.

ReportLab is the one dependency, and an optional one: imported here and
nowhere else, and HAS_REPORTLAB says whether it is there. Without it the
program runs, and the menu says why there is no report.
"""

import datetime

from pressure.scale import Scale
from pressure.timeline import Timeline
from version import APP_NAME, __version__

# Why it is here: tables, flowing pages and vector drawing in a PDF, which
# the standard library does not do. Optional, so a machine without it still
# keeps its diary.
try:
    from reportlab.graphics.shapes import (Circle, Drawing, Line, Rect,
                                           String)
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                    Table, TableStyle)
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# Greys chosen far apart: on a laser printer two colours that are obvious on
# screen arrive within a few points of each other.
INK = "#000000"
MID = "#606060"
LIGHT = "#c8c8c8"
PAPER = "#ffffff"

# The chart, in millimetres: the width of the text block, and a height that
# leaves room for the table under it on the first page.
CHART_HEIGHT_MM = 75
CHART_MARGIN_MM = (12, 4, 10, 8)  # left, right, top, bottom

# The type of the chart, the same as the tables': ReportLab's drawing
# would otherwise write in Times.
FONT = "Helvetica"
FONT_SIZE = 7

# Half the side of a mark on the chart, in points.
MARK = 2.2

SEATED = 1


class Report:
    """One period of the diary, written as a PDF."""

    def __init__(self, engine):
        self.engine = engine

    def write(self, path, period):
        """Write the report of period, (first day, last day), to path."""
        start, end = period
        readings = list(reversed(self.engine.get_readings(start, end)))
        threshold = self.engine.get_threshold()
        styles = getSampleStyleSheet()
        document = SimpleDocTemplate(path, pagesize=A4,
                                     leftMargin=18 * mm, rightMargin=18 * mm,
                                     topMargin=16 * mm, bottomMargin=18 * mm,
                                     title="Blood pressure diary",
                                     author=APP_NAME)
        width = A4[0] - 36 * mm
        story = self.get_heading(styles, period, threshold)
        if readings:
            story.append(self.get_statistics(period))
            story.append(Spacer(1, 6 * mm))
            story.append(self.get_chart(readings, threshold, period, width))
            story.append(Spacer(1, 6 * mm))
            story.append(self.get_readings(readings, threshold))
        else:
            story.append(Paragraph("No readings in the period.",
                                   styles["Normal"]))
        document.build(story, onFirstPage=self.on_page,
                       onLaterPages=self.on_page)

    def get_heading(self, styles, period, threshold):
        name = self.engine.get_setting("patient_name")
        # The program's name first: whoever reads the paper knows what
        # wrote it before reading what it says.
        subtitle = ParagraphStyle("Subtitle", parent=styles["Heading2"],
                                  alignment=TA_CENTER, spaceBefore=0)
        lines = [Paragraph(APP_NAME, styles["Title"]),
                 Paragraph("Home blood pressure diary", subtitle)]
        facts = "From {0} to {1}. Printed {2}.".format(
            self.engine.get_shown_day(period[0]),
            self.engine.get_shown_day(period[1]),
            self.engine.get_shown_day(datetime.date.today()))
        if name:
            facts = "<b>{0}</b>. {1}".format(self.get_escaped(name), facts)
        lines.append(Paragraph(facts, styles["Normal"]))
        lines.append(Paragraph(
            "Readings at or over {0} - either value - are in bold and"
            " marked *. The threshold is the one set in the diary; at home"
            " the ESH 2021 threshold is 135/85 mmHg.".format(
                threshold.get_caption()), styles["Normal"]))
        lines.append(Spacer(1, 5 * mm))
        return lines

    def get_escaped(self, text):
        """Text safe inside a Paragraph, which reads a little markup."""
        return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))

    def get_caption(self, mean, low, high):
        """Mean with its range, rounded half up as on screen."""
        return "{0} ({1}-{2})".format(int(mean + 0.5), low, high)

    def get_statistics(self, period):
        rows = [("Position", "Readings", "Systolic mmHg", "Diastolic mmHg",
                 "Heart rate bpm")]
        for row in self.engine.get_statistics(*period):
            rows.append((row["position"], str(row["readings"]),
                         self.get_caption(row["systolic_mean"],
                                          row["systolic_min"],
                                          row["systolic_max"]),
                         self.get_caption(row["diastolic_mean"],
                                          row["diastolic_min"],
                                          row["diastolic_max"]),
                         self.get_caption(row["heart_rate_mean"],
                                          row["heart_rate_min"],
                                          row["heart_rate_max"])))
        table = Table(rows, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 9)]))
        return table

    def get_readings(self, readings, threshold):
        """Every reading, oldest first; strings in the cells, not
        Paragraphs, so the table's own FONTNAME reaches them."""
        rows = [("", "Date", "Time", "Position", "Systolic", "Diastolic",
                 "Heart rate")]
        commands = [("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK),
                    ("ALIGN", (4, 0), (-1, -1), "RIGHT"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]
        for number, row in enumerate(readings, start=1):
            moment = self.engine.get_moment(row["recorded_at"])
            mark = ""
            if threshold.is_over(row["systolic_mmhg"],
                                 row["diastolic_mmhg"]):
                mark = "*"
                commands.append(("FONTNAME", (0, number), (-1, number),
                                 "Helvetica-Bold"))
            rows.append((mark, self.engine.get_shown_day(moment),
                         moment.strftime("%H:%M:%S"), row["position"],
                         str(row["systolic_mmhg"]),
                         str(row["diastolic_mmhg"]),
                         str(row["heart_rate_bpm"])))
        table = Table(rows, hAlign="LEFT", repeatRows=1)
        table.setStyle(TableStyle(commands))
        return table

    # --- the chart -----------------------------------------------------------

    def get_chart(self, readings, threshold, period, width):
        """The readings drawn as on screen, in points on a Drawing."""
        height = CHART_HEIGHT_MM * mm
        left, right, top, bottom = [value * mm for value in CHART_MARGIN_MM]
        drawing = Drawing(width, height)
        box = (left, bottom, width - right, height - top)
        systolic = [row["systolic_mmhg"] for row in readings]
        diastolic = [row["diastolic_mmhg"] for row in readings]
        scale = Scale(min(diastolic + [threshold.diastolic_mmhg]),
                      max(systolic + [threshold.systolic_mmhg]))
        timeline = Timeline(*period)

        self.set_axes(drawing, box, scale, timeline)
        for value in (threshold.systolic_mmhg, threshold.diastolic_mmhg):
            y = self.get_y(box, scale, value)
            drawing.add(Line(box[0], y, box[2], y, strokeColor=INK,
                             strokeWidth=0.6, strokeDashArray=(4, 3)))
            self.add_text(drawing, box[2] - 2, y + 2, str(value), "end")
        for row in readings:
            moment = self.engine.get_moment(row["recorded_at"])
            x = self.get_x(box, timeline, moment)
            high = self.get_y(box, scale, row["systolic_mmhg"])
            low = self.get_y(box, scale, row["diastolic_mmhg"])
            drawing.add(Line(x, low, x, high, strokeColor=LIGHT,
                             strokeWidth=0.8))
            self.add_circle(drawing, x, high, row["position_id"])
            self.add_square(drawing, x, low, row["position_id"])
        self.add_legend(drawing, box, height)
        return drawing

    def set_axes(self, drawing, box, scale, timeline):
        x0, y0, x1, y1 = box
        for value in scale.get_ticks():
            y = self.get_y(box, scale, value)
            drawing.add(Line(x0, y, x1, y, strokeColor=LIGHT,
                             strokeWidth=0.3))
            self.add_text(drawing, x0 - 3, y - 2.5, str(value), "end")
        for day in timeline.get_ticks():
            moment = timeline.first + (day - timeline.start)
            x = self.get_x(box, timeline, moment)
            drawing.add(Line(x, y0, x, y0 - 2, strokeColor=INK,
                             strokeWidth=0.5))
            self.add_text(drawing, x, y0 - 9, day.strftime("%d/%m"),
                          "middle")
        drawing.add(Rect(x0, y0, x1 - x0, y1 - y0, fillColor=None,
                         strokeColor=INK, strokeWidth=0.6))
        self.add_text(drawing, x0 - 3, y1 + 7, "mmHg", "end")

    def get_fill(self, position_id, ink):
        fill = PAPER
        if position_id == SEATED:
            fill = ink
        return colors.HexColor(fill)

    def add_circle(self, drawing, x, y, position_id):
        """Systolic: a circle."""
        drawing.add(Circle(x, y, MARK, fillColor=self.get_fill(position_id,
                                                               INK),
                           strokeColor=colors.HexColor(INK),
                           strokeWidth=0.7))

    def add_square(self, drawing, x, y, position_id):
        """Diastolic: a square, so a grey printer cannot confuse the two."""
        drawing.add(Rect(x - MARK, y - MARK, 2 * MARK, 2 * MARK,
                         fillColor=self.get_fill(position_id, MID),
                         strokeColor=colors.HexColor(MID), strokeWidth=0.7))

    def add_legend(self, drawing, box, height):
        y = height - 3 * mm
        x = box[0]
        self.add_circle(drawing, x + MARK, y, SEATED)
        self.add_text(drawing, x + 3 * MARK, y - 2.5, "systolic")
        x += 18 * mm
        self.add_square(drawing, x + MARK, y, SEATED)
        self.add_text(drawing, x + 3 * MARK, y - 2.5, "diastolic")
        x += 20 * mm
        self.add_text(drawing, x, y - 2.5, "filled: seated, hollow: lying;"
                      " dashed: the threshold")

    def add_text(self, drawing, x, y, text, anchor="start"):
        drawing.add(String(x, y, text, fontName=FONT, fontSize=FONT_SIZE,
                           textAnchor=anchor))

    def get_y(self, box, scale, value):
        return box[1] + scale.calc_fraction(value) * (box[3] - box[1])

    def get_x(self, box, timeline, moment):
        return box[0] + timeline.calc_fraction(moment) * (box[2] - box[0])

    # --- every page ----------------------------------------------------------

    def on_page(self, canvas, document):
        """The foot of every page: what wrote it, what it is not, which page.
        """
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.drawString(18 * mm, 10 * mm,
                          "{0} {1} - it records and shows; it does not"
                          " diagnose.".format(APP_NAME, __version__))
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm,
                               "page {0}".format(document.page))
        canvas.restoreState()
