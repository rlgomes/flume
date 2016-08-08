"""
flume moment module

- used to simplify the representation of dates and durations by easily
  parseable human expressions
"""

from datetime import datetime, timedelta
from time import mktime

import parsedatetime
import pytz

from delta import parse
from dateutil import parser

from flume.exceptions import FlumineException
from flume.util import is_string


def __make_utc(dt):
    """
    localize or attach the UTC timezone to the datetime object provided
    """
    return pytz.UTC.localize(dt)

__MIN = __make_utc(datetime(1900, 1, 1))
__MAX = __make_utc(datetime.max)


def now():
    """
    returns a datetime object that represents the current time
    """
    return __make_utc(datetime.now())


def beginning():
    """
    returns a datetime object that represents the beginning of time
    """
    return __MIN


def end():
    """
    returns a datetime object that represents the end of time
    """
    return __MAX


def forever():
    """
    returns a timedelta that represents forever """
    return timedelta.max


def date(string):
    """
    returns the datetime associated with the date expressed in the string
    provided. You can express time with an exactly ISO8601 date or you can
    also express it using relative time expression such as '1 hour ago'
    """
    if isinstance(string, datetime):
        return string

    elif is_string(string):
        dt = None
        try:
            dt = parser.parse(string)
        except ValueError as exception:
            if str(exception) == 'Unknown string format':
                # lets parse the possible relative time with parsedatetime
                struct_time, result = parsedatetime.Calendar().parse(string)

                if result == 0:
                    raise FlumineException('unable to parse date "%s"' % string)

                dt = datetime.fromtimestamp(mktime(struct_time))

        if dt is None:
            raise FlumineException('Unable to parse moment "%s"' % string)

        if dt.tzinfo is None:
            # all dates without a timezone are assumed to be in UTC
            dt = __make_utc(dt)

        return dt
    else:
        raise FlumineException('Unable to parse moment "%s"' % string)

def duration(string, context=None):
    """
    Converts a string representing a duration into a timedelta

    arguments:

        string - The string to convert into seconds representing the duration
                 expressed in natural human language, ie 1 hour, 1h, 2 days,
                 etc.

        context - Datetime object expressing the context to evaluate the
                  duration string in. This really applies to things like
                  `1 month` in the context of January has 31 days vs April has
                  30 days. Defaults to datetime.now()
    returns:

        Number of seconds represented by the duration string provided
    """
    if isinstance(string, timedelta):
        return string

    elif is_string(string):
        delta = parse(string, context=context)

        if delta is None:
            raise FlumineException('unable to parse the duration "%s"' % string)

        return delta

    raise FlumineException('unable to parse the duration "%s"' % string)

def datetime_to_iso8601(dt):
    """
    Convert a datetime into the ISO8601 string that it represents
    """
    return '%s.%03dZ' % (dt.strftime('%Y-%m-%dT%H:%M:%S'),
                         int(dt.microsecond / 1000))
