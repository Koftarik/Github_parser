from datetime import date, timedelta, datetime


def get_date_intervals(start_date: str | None, end_date: str | None = None, delta_days=14):
    if start_date is None:
        start_inc_date = datetime.strptime('2013-01-01', '%Y-%m-%d')
    else:
        start_inc_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is None:
        stop_date = date.today()
    else:
        stop_date = datetime.strptime(end_date, '%Y-%m-%d')

    dates = []
    while start_inc_date < stop_date:
        dates.append((start_inc_date, start_inc_date + timedelta(days=delta_days)))
        start_inc_date += timedelta(days=delta_days)
    return dates
