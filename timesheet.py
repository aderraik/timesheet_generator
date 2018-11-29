# Timesheet generation script for Hiwis.
# imports
import datetime
import argparse
import holidays
import calendar
import numpy as np
import random


###
# Use following section to set your personal default values!
###
default_hours = 23
default_days_of_week = [0, 1, 2, 3, 4]
default_start_hour = 8
default_end_hour = 18
default_max_hours = 6
default_output_file_name = 'timesheet'
default_state = 'RJ'

# current-date relative defaults
default_month = datetime.date.today().month
default_year = datetime.date.today().year
default_fdom = 1
default_ldom = datetime.date.today().day - 1

###
# PARSE ARGUMENTS
###

# parse arguments
parser = argparse.ArgumentParser(description='Generate Random Timesheets.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-y', help='year (defaults to current)', type=int, default=default_year)
parser.add_argument('-m', help='month (defaults to current)', type=int, default=default_month)
parser.add_argument('-fdom', help='first day of the month that should be used (defaults to beginning of month)',
                    type=int, default=default_fdom)
parser.add_argument('-ldom', help='last day of the month that should be used (defaults to yesterday)', type=int,
                    default=default_ldom)
parser.add_argument('-dow', help='days of the week (monday = 0, tuesday = 1, ...)', type=int, nargs='*',
                    default=default_days_of_week)
parser.add_argument('-hrs', help='number of hours to distribute', type=float, default=default_hours)
parser.add_argument('-s', help='start time', type=int, default=default_start_hour)
parser.add_argument('-e', help='end time', type=int, default=default_end_hour)
parser.add_argument('-max', help='maximum hours for a day', type=int, default=default_max_hours)
parser.add_argument('-o', help='output file name', default=default_output_file_name)
parser.add_argument('-state',
                    help='brazilian state for public holiday considerations, from list: AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO',
                    default=default_state)

args = parser.parse_args()

# get parsed arguments
year = args.y
month = args.m
days_of_week = args.dow
hours = args.hrs
work_start = args.s
max_hours = args.max
work_end = args.e
filename = args.o
ldom = args.ldom


###
# HELPER FUNCTIONS
###

def format_timedelta(td):
    """Format datetime.timedelta as "hh:mm"."""
    s = td.total_seconds()
    return "{:0>2d}:{:0>2d}".format(int(s // 3600), int((s % 3600) // 60))


def weighted_choice(choices):
    """Select random choice from list of (option, weight) pairs according to the weights."""
    choices = list(choices)
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c, w
        upto += w
    return c, w


###
# DATA GENERATION
###

# get public holidays and length of the month
public_holidays = holidays.BR(state=args.state, years=year)
days_in_month = calendar.monthrange(year, month)[1]

# check which days are valid, i.e. are specified workdays and not holidays
valid_days = []
for day in range(args.fdom, min(days_in_month, ldom) + 1):
    date = datetime.date(year, month, day)
    if date not in public_holidays and date.weekday() in days_of_week:
        valid_days.append(day)

# Distribute hours over valid days. Use exponential weights (after random shuffle) for days,
# so some days are used often and some are used rarely.
possible_days = valid_days
random.shuffle(possible_days)
weights = list(1 / np.arange(1, len(possible_days) + 1))

# collector for sampled distribution
# day => (start, end)
collector = dict()

# possible chunks over the day are from start to end in steps of half-hours
chunk_starts = np.arange(work_start, work_end, 0.5)

# distribute all hours
h = hours
while h > 0:
    if len(possible_days) == 0:
        raise RuntimeError("Could not work off all hours with given parameters!")
    # select day
    day, weight = weighted_choice(zip(possible_days, weights))
    # if day is already listed, extend working hours there either before or after
    if day in collector:
        start, end = collector[day]
        possible_extensions = []
        if start > work_start:
            possible_extensions.append('before')
        if end < (work_end - 0.5):
            possible_extensions.append('after')
        extension = random.choice(possible_extensions)
        if extension == 'before':
            start -= 0.5
        if extension == 'after':
            end += 0.5
        collector[day] = (start, end)
        if end - start == max_hours:
            possible_days.remove(day)
            weights.remove(weight)
    # if day not yet listed, select random starting chunk
    else:
        start = random.choice(chunk_starts)
        end = start + 0.5
        collector[day] = (start, end)
    # half and hour was distributed off
    h -= 0.5

###
# FORMATTING DATA
###

# extract relevant data from work distribution
# list entries are strings: (day, start_time, end_time, duration, recording_date)
data = []
for day in range(1, days_in_month + 1):
    date = datetime.date(year, month, day)
    if day in collector:
        s, e = collector[day]
        s_h = int(s)
        s_m = int((s % 1) * 60)
        e_h = int(e)
        e_m = int((e % 1) * 60)
        start = datetime.datetime.combine(date, datetime.time(s_h, s_m))
        end = datetime.datetime.combine(date, datetime.time(e_h, e_m))
        duration = end - start
        data.append((
            date.strftime("%d.%m"),
            start.strftime("%H:%M"),
            end.strftime("%H:%M"),
            format_timedelta(duration),
        ))
    else:
        data.append((
            date.strftime("%d.%m"),
            "",
            "",
            "",
            ""
        ))

# additional format strings
header_date = "{:0>2d}/{}".format(month, year)
total_hours_formatted = format_timedelta(datetime.timedelta(hours=hours))

###
# TEMPLATE
###

entry_template = "{}\t{}\t{}\t{}\n"

###
# BUILD
###

# write template to file and fill it with the data
with open("{}.csv".format(filename), "w") as f:
    for entries in data:
        f.write(entry_template.format(*entries))
    f.write(total_hours_formatted)
