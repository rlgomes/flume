"""
date reducer - exposes the date manipulation functions as reducers
"""
import inspect

from flume import reducer


def strftime(fieldname, fmt):

    class strftime_reducer(reducer):

        def __init__(self, fieldname, fmt):
            self.fieldname = fieldname
            self.fmt = fmt
            self.value = None

        def update(self, point):
            self.value = point[self.fieldname].strftime(self.fmt)

        def result(self):
            return self.value

        def reset(self):
            self.value = None

    return strftime_reducer(fieldname, fmt)

class date(object):

    @classmethod
    def year(cls, fieldname):
        """
        return the year for the field specified. example: 2010, 2016, etc.
        """
        return strftime(fieldname, '%Y')

    @classmethod
    def fullmonth(cls, fieldname):
        """
        return the full month name for the field specified. example: January
        """
        return strftime(fieldname, '%B')

    @classmethod
    def month(cls, fieldname):
        """
        return the abbreviated month name for the field specified. example: Jan
        """
        return strftime(fieldname, '%b')

    @classmethod
    def fullweekday(cls, fieldname):
        """
        return the full weekday name for the field specified. example: Sunday
        """
        return strftime(fieldname, '%A')

    @classmethod
    def weekday(cls, fieldname):
        """
        return the abbreviated weekday name for the field specified. example: Sun
        """
        return strftime(fieldname, '%a')

    @classmethod
    def strftime(cls, fieldname, fmt):
        """
        return the strftime format(fmt) applied to the field name provided
        (must be a datetime object) format details: https://goo.gl/r8rDLB
        """
        return strftime(fieldname, fmt)
