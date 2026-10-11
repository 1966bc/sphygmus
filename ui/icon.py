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
        "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA6klEQVR42mNgoBY4oaCj"
        "AMTzgfg+EJ+HshWQxM9D5cDi6JoFgPg9EP9Hw+/xiAsgGzAfiyIwfrdz7//TepbY5OYj"
        "G3AelwEgcC0iEZvceWQDsGq+5BUCNuBBUwdWeWQD9iNLPJkwDWwrCIPAq9UbsBmwH9mA"
        "fnRbv169Drb5x+On/z8eP4XNgH64AUD1Cv+RAEgjyAAQfj53MVjsz8dP/9EARlT2o3sD"
        "BG6m5YE1g/hYbUczBB4bII2wGACxkaLyPL7UKAAzBKQBBNCjDiUB4TFkPSxAkTSvJ6gZ"
        "zaACpKRcQG4GMwBhBloCAIMWZti0KUToAAAAAElFTkSuQmCC"
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABw0lEQVR42u1XPUvEQBC9"
        "n5CfkB8gklawtrC2sIyNpWxhZxOsLK3sJIWlRWwtjpSKFgFBxUJOUBEsXE4QLIS4TzJh"
        "79ivSU5BuAdT3GVn5+XtfGwGgzksOI8XImVCWaGsbCxXljp80mYNrS+aPSJu8EyZVFZb"
        "DM+Etl4ErM9Cg+eOjaYt5673BReMzbqacBGQ3A2vVtfqh909jo90JRD7jT6ub2vgZn2D"
        "45f2PfvWCEwVchOBkhv8cnGpJfB6fMLxLWdCALITxmcXf0/gfnun1tGXQOFzxDlXyyvt"
        "76f9gwkC+jOPFbbuZ3WiYLrUb6fDCQJ3m1uhBDITgcTmgDf7Gr+3gSA9/gcZgEoRJAMJ"
        "JLZeMDI5IMMBIvH5+PxTAfSbnkORgOAjaydUe4jaASiB4FT3BKoGKEFqOCBcBCJl0uT1"
        "cnhkzHxSIxDYO+o1kKCCDkpKUkbPEdYg4vQEPSGpA+oJGVz7DgKxazLq5UeZjxKECpiO"
        "lgtJzL0VJb6ewKj9pOu9MPXNgIAxnPa9nKam4wjo/7J38KnjmCAB6R3yy86ye67pIROz"
        "ZF/DO1zZw4fML5HAkVRa4GrmkjO+IfL5d+S/xjduNV05jRNtBAAAAABJRU5ErkJggg=="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAACjElEQVR42u1ZvUrEQBDO"
        "I+QR8gAi1woWqSysrrCwjI2lXGFnE6zsYmUnV1haxNZCUipaBAQVC4mgIlh4nCBYCDED"
        "uzDu5ZLZzWxyRT7Y4rhkdr7d+Y/j9OjRHq68Jb9YYbGiYiXFisXvoFiuhhxXvBMKGYmQ"
        "Cb99bqVdITgrVl6zkioFxAEkBDmZ2NNtqvyAqHgZkYEiJzGQk2E5JspPDDaVayJksMjR"
        "Vd5ruCnenEuOp0MgYdiUeyVU5QPuzW/XN/J0dY1DVtD66b8eHuWA3+kXB4mEYvuspz+9"
        "vM4lnvcPOGR6rZoPnLzEx+mZXTMSyYOVAAbcBoPMsIpAzKn8/eZWroJBbtyaA5cRsOrI"
        "tiIQxuP2jlUCrCb0fnwyQwBI2TSh0DRR1YVQic/zC6tOrB1Gv+8e5kaYn5e3GQLwvM0w"
        "qpXInnb3Ku17HqwlMkGCVP/fLK/8S1IAOHH5P0SbeYDoZKh8RqmFItMIg50Uh1AwG+wP"
        "cHOGBCJqI1MpSD1d6QeyaIPbgboHZ2AckRpEIlpjA/kmJwLMRjUnqHnwDYHyVYSISMkN"
        "TfFwQJUq7Rk7NJDBJgNksEmpvkNEoNVWFi9kdRLV6hIDKwnKwy01QGY6AzKu/TFkoivL"
        "C8SI5JtOJuKmpQOO+ypBYn8QNx1qkacKkMhUgCmVhV5iiznhGG6RTakseeESAzsyMZT6"
        "XOPFEZWEaueqmYA/EO1+xD0jHVMIQLXJUD6PbU2na0nghGXYwNhRnkpCbSM1Cze7ylNJ"
        "YEACWyjlKd0blBUQfTQGWWFXX2yGDKPzYdefnaCLSw2UT7VG5l2a1MKYDDFrZzWfjHxn"
        "kSHqp7K2NGpc13Tk4N07akOT8p0ePXpYwx/Z3fE8P1U4PwAAAABJRU5ErkJggg=="
    ),
    (
        "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAADT0lEQVR42u1bP6vUQBDf"
        "j/A+Qj6AyLWCRSoLq1dYWJ6NpZWdzWJld1Z2ksLSIrYW8kpFi4CgYiERVAQLjycIFkLM"
        "wC7krbO57OzMJrnkB8Pj8i67O7/Mzr/NKbVixYoVRLzKLp20kreiEYHrJ3OYg7KobStl"
        "K80Aqcxis4DxM3NPNXAOWMs2heLAeD1wUZgUfUQYxYuI8WFtuZTyu4iFuaKR8TXj+Dvu"
        "fX7GuDgrZ2Zs0fE5CCgEFtfdu6Xg+EWs8lpwcalEU5XPjkB5K9nUTD+1FJN9+m8uX2nO"
        "X75uAPAXPo9uBcwhr1e+P37SdPH5/gOpuXYhBNSpCLBP3wIIEZqrnqTz+/3uwwUCgJBR"
        "naFJd5MRgEFwvnxSsb+6eg0lAK6PlhOkJOD9zVsoAXB9EQSAx8fw9eGjZRAAimL4+fzF"
        "MggARTFAZFgEAW4OkCAS6KHtrtFCoMXb6zck5twmyQMgnwfz/nv+y+vQ4Dt9+HT33jh5"
        "gCGB1bSxsOYLgZKRIKQWqDhj+58v3/773sfbd3oJEEiJqyTVICiLwa3y3BAI2+UQaSmr"
        "wZwzsbEKdmv9H0+fXfi/+xnA3BvIQ5sidajjc5+ii26p6/oJIM+9nzElrsXPAdzGht3H"
        "vkIHUxYjZbRzgnb+rIkAmDRmFda5YcS4JMJncJaHLGsAMlJnuL2xpMzW3e9Yvg8xHsv8"
        "XB8CKbHPqQagJJ8LtDfnlBndGO4q4To8m/sfyg2IiDsrDLUCrKeHeXhfzGdGqWLB0SPE"
        "TN5Hms/kYVsROkWZ4kBshQiFzdAt46sQCamxVlwwJ7hRrfI+T96N95jTBKsITIpq9jdH"
        "2gE3UrV/t/TFagS4FjjfRuolCc3d/nKbH26nmFAUaSUJ6nm+L8TB1sAqRVAcegqBpl8q"
        "aRh/UFGaJMJlb5XsjTETGvexx2A2KWJQfs8W8gKdYhAJWELE0PnZizk9bhKwhIjg4aeh"
        "PIUELCGKqPnHV94hoaYkRMSuTz0Z5UOjA2wDSwKx9Z3O2xNJkHy5qpis8glOl7ZqTjB+"
        "oWJKcDZqjjBbIuaNs90sTF7gNXu5195n4CCLo3jqPUScehInuHaqlgAkZ6iO+qn3kGB/"
        "L7As5R0Slqn8ihUrVkwB/wA+KSozAqzKgQAAAABJRU5ErkJggg=="
    ),
    (
        "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"
        "zFOs+2RMAAAAAElFTkSuQmCC"
    ),
)
