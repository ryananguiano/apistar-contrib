from datetime import datetime, timedelta, tzinfo
from apistar_contrib.compat import pytz


ZERO = timedelta(0)


class UTC(tzinfo):
    """
    UTC implementation taken from Python's docs.

    Used only when pytz isn't available.
    """

    def __repr__(self):
        return "<UTC>"

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = pytz.utc if pytz else UTC()


def is_aware(value):
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None


def is_naive(value):
    return value.tzinfo is None or value.tzinfo.utcoffset(value) is None


def make_aware(value, timezone=None):
    """
    Makes a naive datetime.datetime in a given time zone aware.
    """
    if timezone is None:
        timezone = utc
    if hasattr(timezone, 'localize'):
        # This method is available for pytz time zones.
        return timezone.localize(value, is_dst=None)
    else:
        # Check that we won't overwrite the timezone of an aware datetime.
        if is_aware(value):
            raise ValueError(
                "make_aware expects a naive datetime, got %s" % value)
        # This may be wrong around DST changes!
        return value.replace(tzinfo=timezone)


def make_naive(value, timezone=None):
    """
    Makes an aware datetime.datetime naive in a given time zone.
    """
    if timezone is None:
        timezone = utc
    # If `value` is naive, astimezone() will raise a ValueError,
    # so we don't need to perform a redundant check.
    value = value.astimezone(timezone)
    if hasattr(timezone, 'normalize'):
        # This method is available for pytz time zones.
        value = timezone.normalize(value)
    return value.replace(tzinfo=None)


def now():
    """
    Returns an aware datetime.datetime.
    """
    # timeit shows that datetime.now(tz=utc) is 24% slower
    return datetime.utcnow().replace(tzinfo=utc)


def localtime(value, timezone):
    value = value.astimezone(timezone)
    if hasattr(timezone, 'normalize'):
        value = timezone.normalize(value)
    return value
