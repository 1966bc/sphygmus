# sphygmus

From the Greek *sphygmós*, the pulse: the root of *sphygmomanometer*.

A home blood pressure diary: Python, Tkinter and SQLite, with a PDF report
to take to the doctor.

> **Status:** design. The schema is written; the program is not yet.

## What it does

- Records each reading as the device shows it: date and time, systolic,
  diastolic, heart rate, and whether it was taken seated or lying down.
- Lists the readings and highlights those at or above the home threshold of
  135/85 mmHg (ESH 2021). The threshold is a setting, not a constant.
- Shows the statistics for a chosen period, by position: number of
  readings, mean, minimum and maximum.
- Draws the readings over time, by hand on a Tkinter canvas.
- Prints a PDF report with ReportLab: the statistics, the chart and every
  reading.

It records and shows. It does not diagnose or advise.

## Why it is written the way it is

The project is small on purpose, and meant to be read. `CONVENTIONS.md`
gives the rules and the reason for each: one field for date and time, no
means stored, the threshold as data, one person and so no patient table.

The general rules come from
[fundamenta](https://github.com/1966bc/fundamenta).

## The database

```bash
sqlite3 diary.sl3 < sql/ddl/001_schema.sql
sqlite3 diary.sl3 < sql/dml/001_master_data.sql
```

The repository carries the schema and invented sample data, never a real
diary.

## Requirements

Python 3.7 or later with Tkinter (`python3-tk` on Debian), and ReportLab for
the report.

## Licence

GPL-3.0-or-later, see `LICENSE`.

Giuseppe Costanzi ([1966bc](https://github.com/1966bc))
