import unittest

from robber import expect
from flume import moment


class MomentTest(unittest.TestCase):

    def test_parsing_iso8601_date(self):
        date1 = moment.date('2016-01-01')
        date2 = moment.date('2016-01-01T00:00:00.000Z')
        expect(date1).to.eq(date2)

    def test_parsing_a_relative_day_ago_date(self):
        date1 = moment.date('1 day ago')
        date2 = moment.date('24 hours ago')
        expect(date1).to.eq(date2)

    def test_parsing_a_relative_year_ago_date(self):
        date1 = moment.date('1 year ago')
        date2 = moment.date('12 months ago')
        expect(date1).to.eq(date2)
