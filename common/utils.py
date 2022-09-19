import calendar
import datetime


def business_days(month, year):
    _, days_in_month = calendar.monthrange(year, month)
    for day in xrange(1, days_in_month + 1):
        date = datetime.date(year, month, day)
        if date.weekday() < 5:
            yield date

def daterange(start_date, end_date):
    for days in xrange(int((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(days)
