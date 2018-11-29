# Generate timesheets for your university hiwi contract.

This will generate a random timesheet with valid working hours for your given parameters. It considers weekends and even public holidays. You will need python3 to run it (see requirements.txt for a list of needed libraries) and pdflatex installed and on your path.

The random sampling works with chunks of 30 minutes that are distributed over all valid days with random starting hours until the specified hours are consumed. The days are weighted according to 1/x for some random order, so some days get a lot of chunks and some get only little.

Many options can be configured though parameters, e.g. you can specify to work only on Mondays and Wednesdays by passing `-dow 0 2`. For continued usage you might want to adjust the default-values directly in your script at the very top.

This tool is only considered for checking the validity of timesheets and not intended for submission.

Have a look at some [example output](example_output.pdf).

```
usage:
python3 timesheet.py [-h] [-y Y] [-m M] [-ldom LDOM]
                     [-dow [DOW [DOW ...]]] [-hrs HRS] [-s S] [-e E]
                     [-max MAX] [-o O] [-state STATE]

Generate University Timesheets.

optional arguments:
  -h, --help            show this help message and exit
  -y Y                  year (defaults to current) (default: 2017)
  -m M                  month (defaults to current) (default: 5)
  -ldom LDOM            last day of the month that should be used (defaults to
                        yesterday) (default: 27)
  -dow [DOW [DOW ...]]  days of the week (monday = 0, tuesday = 1, ...)
                        (default: [0, 1, 2, 3, 4])
  -hrs HRS              hours (default: 24)
  -s S                  start time (default: 8)
  -e E                  end time (default: 20)
  -max MAX              maximum hours for a day (default: 6)
  -o O                  output file name (default: timesheet)
  -state STATE          german state for public holiday considerations, from
                        list: AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PE, PI,
                        RJ, RN, RS, RO, RR, SC, SP, SE, TO (default: RJ)

```
