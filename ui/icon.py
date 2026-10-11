# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  sphygmus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  GPL-3.0-or-later, see LICENSE
# -----------------------------------------------------------------------------
"""The icon: a red heart crossed by a white pulse trace.

Written by forge/make_icon.py, which draws it with no imaging
library; not edited by hand. PNG in base64, one per size, so
the program needs no file beside it and Tk reads them as they
are: tk.PhotoImage(data=...).
"""

# Sizes 16, 32, 48, 64, 128, in that order.
ICONS = (
    (
        "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA6klEQVR42mNgoBY4oaCjAM"
        "Tzgfg+EJ+HshWQxM9D5cDi6JoFgPg9EP9Hw+/xiAsgGzAfiyIwfrdz7//TepbY5OYjG3Ae"
        "lwEgcC0iEZvceWQDsGq+5BUCNuBBUwdWeWQD9iNLPJkwDWwrCIPAq9UbsBmwH9mAfnRbv1"
        "69Drb5x+On/z8eP4XNgH64AUD1Cv+RAEgjyAAQfj53MVjsz8dP/9EARlT2o3sDBG6m5YE1"
        "g/hYbUczBB4bII2wGACxkaLyPL7UKAAzBKQBBNCjDiUB4TFkPSxAkTSvJ6gZzaACpKRcQG"
        "4GMwBhBloCAIMWZti0KUToAAAAAElFTkSuQmCC"
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABw0lEQVR42u1XPUvEQBC9n5"
        "CfkB8gklawtrC2sIyNpWxhZxOsLK3sJIWlRWwtjpSKFgFBxUJOUBEsXE4QLIS4TzJh79iv"
        "SU5BuAdT3GVn5+XtfGwGgzksOI8XImVCWaGsbCxXljp80mYNrS+aPSJu8EyZVFZbDM+Etl"
        "4ErM9Cg+eOjaYt5673BReMzbqacBGQ3A2vVtfqh909jo90JRD7jT6ub2vgZn2D45f2PfvW"
        "CEwVchOBkhv8cnGpJfB6fMLxLWdCALITxmcXf0/gfnun1tGXQOFzxDlXyyvt76f9gwkC+j"
        "OPFbbuZ3WiYLrUb6fDCQJ3m1uhBDITgcTmgDf7Gr+3gSA9/gcZgEoRJAMJJLZeMDI5IMMB"
        "IvH5+PxTAfSbnkORgOAjaydUe4jaASiB4FT3BKoGKEFqOCBcBCJl0uT1cnhkzHxSIxDYO+"
        "o1kKCCDkpKUkbPEdYg4vQEPSGpA+oJGVz7DgKxazLq5UeZjxKECpiOlgtJzL0VJb6ewKj9"
        "pOu9MPXNgIAxnPa9nKam4wjo/7J38KnjmCAB6R3yy86ye67pIROzZF/DO1zZw4fML5HAkV"
        "Ra4GrmkjO+IfL5d+S/xjduNV05jRNtBAAAAABJRU5ErkJggg=="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAACjElEQVR42u1ZvUrEQBDOI+"
        "QR8gAi1woWqSysrrCwjI2lXGFnE6zsYmUnV1haxNZCUipaBAQVC4mgIlh4nCBYCDEDuzDu"
        "5ZLZzWxyRT7Y4rhkdr7d+Y/j9OjRHq68Jb9YYbGiYiXFisXvoFiuhhxXvBMKGYmQCb99bq"
        "VdITgrVl6zkioFxAEkBDmZ2NNtqvyAqHgZkYEiJzGQk2E5JspPDDaVayJksMjRVd5ruCne"
        "nEuOp0MgYdiUeyVU5QPuzW/XN/J0dY1DVtD66b8eHuWA3+kXB4mEYvuspz+9vM4lnvcPOG"
        "R6rZoPnLzEx+mZXTMSyYOVAAbcBoPMsIpAzKn8/eZWroJBbtyaA5cRsOrItiIQxuP2jlUC"
        "rCb0fnwyQwBI2TSh0DRR1YVQic/zC6tOrB1Gv+8e5kaYn5e3GQLwvM0wqpXInnb3Ku17Hq"
        "wlMkGCVP/fLK/8S1IAOHH5P0SbeYDoZKh8RqmFItMIg50Uh1AwG+wPcHOGBCJqI1MpSD1d"
        "6QeyaIPbgboHZ2AckRpEIlpjA/kmJwLMRjUnqHnwDYHyVYSISMkNTfFwQJUq7Rk7NJDBJg"
        "NksEmpvkNEoNVWFi9kdRLV6hIDKwnKwy01QGY6AzKu/TFkoivLC8SI5JtOJuKmpQOO+ypB"
        "Yn8QNx1qkacKkMhUgCmVhV5iiznhGG6RTakseeESAzsyMZT6XOPFEZWEaueqmYA/EO1+xD"
        "0jHVMIQLXJUD6PbU2na0nghGXYwNhRnkpCbSM1Cze7ylNJYEACWyjlKd0blBUQfTQGWWFX"
        "X2yGDKPzYdefnaCLSw2UT7VG5l2a1MKYDDFrZzWfjHxnkSHqp7K2NGpc13Tk4N07akOT8p"
        "0ePXpYwx/Z3fE8P1U4PwAAAABJRU5ErkJggg=="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAADT0lEQVR42u1bP6vUQBDfj/"
        "A+Qj6AyLWCRSoLq1dYWJ6NpZWdzWJld1Z2ksLSIrYW8kpFi4CgYiERVAQLjycIFkLMwC7k"
        "rbO57OzMJrnkB8Pj8i67O7/Mzr/NKbVixYoVRLzKLp20kreiEYHrJ3OYg7KobStlK80Aqc"
        "xis4DxM3NPNXAOWMs2heLAeD1wUZgUfUQYxYuI8WFtuZTyu4iFuaKR8TXj+DvufX7GuDgr"
        "Z2Zs0fE5CCgEFtfdu6Xg+EWs8lpwcalEU5XPjkB5K9nUTD+1FJN9+m8uX2nOX75uAPAXPo"
        "9uBcwhr1e+P37SdPH5/gOpuXYhBNSpCLBP3wIIEZqrnqTz+/3uwwUCgJBRnaFJd5MRgEFw"
        "vnxSsb+6eg0lAK6PlhOkJOD9zVsoAXB9EQSAx8fw9eGjZRAAimL4+fzFMggARTFAZFgEAW"
        "4OkCAS6KHtrtFCoMXb6zck5twmyQMgnwfz/nv+y+vQ4Dt9+HT33jh5gCGB1bSxsOYLgZKR"
        "IKQWqDhj+58v3/773sfbd3oJEEiJqyTVICiLwa3y3BAI2+UQaSmrwZwzsbEKdmv9H0+fXf"
        "i/+xnA3BvIQ5sidajjc5+ii26p6/oJIM+9nzElrsXPAdzGht3HvkIHUxYjZbRzgnb+rIkA"
        "mDRmFda5YcS4JMJncJaHLGsAMlJnuL2xpMzW3e9Yvg8xHsv8XB8CKbHPqQagJJ8LtDfnlB"
        "ndGO4q4To8m/sfyg2IiDsrDLUCrKeHeXhfzGdGqWLB0SPETN5Hms/kYVsROkWZ4kBshQiF"
        "zdAt46sQCamxVlwwJ7hRrfI+T96N95jTBKsITIpq9jdH2gE3UrV/t/TFagS4FjjfRuolCc"
        "3d/nKbH26nmFAUaSUJ6nm+L8TB1sAqRVAcegqBpl8qaRh/UFGaJMJlb5XsjTETGvexx2A2"
        "KWJQfs8W8gKdYhAJWELE0PnZizk9bhKwhIjg4aehPIUELCGKqPnHV94hoaYkRMSuTz0Z5U"
        "OjA2wDSwKx9Z3O2xNJkHy5qpis8glOl7ZqTjB+oWJKcDZqjjBbIuaNs90sTF7gNXu5195n"
        "4CCLo3jqPUScehInuHaqlgAkZ6iO+qn3kGB/L7As5R0Slqn8ihUrVkwB/wA+KSozAqzKgQ"
        "AAAABJRU5ErkJggg=="
    ),
    (
        "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"
        "V4zFOs+2RMAAAAAElFTkSuQmCC"
    ),
)
