import calendar
from datetime import datetime

from apistar_contrib.timezone import utc


def dt_to_unix(dt):
    if isinstance(dt, datetime):
        dt = calendar.timegm(dt.utctimetuple())
    return dt


def dt_to_unix_ms(dt):
    return int(dt_to_unix(dt) * 1e3)


def dt_to_unix_us(dt):
    return int(dt_to_unix(dt) * 1e6)


def unix_to_dt(dt):
    if isinstance(dt, (int, float)):
        try:
            dt = datetime.fromtimestamp(dt, utc)
        except ValueError:
            try:
                dt = datetime.fromtimestamp(dt / 1e3, utc)
            except ValueError:
                dt = datetime.fromtimestamp(dt / 1e6, utc)
    return dt
