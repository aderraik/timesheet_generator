#!/usr/bin/env bash

YEAR=2018
MONTH=11
LAST_DAY_OF_MONTH=30
NUM_OF_HOURS=150

python timesheet.py -y ${YEAR} -m ${MONTH} -ldom ${LAST_DAY_OF_MONTH} -hrs ${NUM_OF_HOURS} -dow 0 1 2 3 4 5 6