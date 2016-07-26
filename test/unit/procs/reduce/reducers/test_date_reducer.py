"""
math reducers unittests
"""
import unittest

from datetime import datetime

from robber import expect
from flume import *


class DateReducerTest(unittest.TestCase):

    def test_date_year(self):
        results = []
        (
            emit(limit=1, start='2016-01-01')
            | put(year=date.year('time'))
            | keep('year')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'year': '2016'}
        ])

    def test_date_fullmonth(self):
        results = []
        (
            emit(limit=1, start='2016-01-01')
            | put(month=date.fullmonth('time'))
            | keep('month')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'month': datetime(2016, 1, 1).strftime('%B')}
        ])

    def test_date_month(self):
        results = []
        (
            emit(limit=1, start='2016-01-01')
            | put(month=date.month('time'))
            | keep('month')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'month': datetime(2016, 1, 1).strftime('%b')}
        ])

    def test_date_fullweekday(self):
        results = []
        (
            emit(limit=1, start='2016-01-01')
            | put(weekday=date.fullweekday('time'))
            | keep('weekday')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'weekday': datetime(2016, 1, 1).strftime('%A')}
        ])

    def test_date_weekday(self):
        results = []
        (
            emit(limit=1, start='2016-01-01')
            | put(weekday=date.weekday('time'))
            | keep('weekday')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'weekday': datetime(2016, 1, 1).strftime('%a')}
        ])

    def test_date_strftime(self):
        results = []
        (
            emit(limit=1, start='2016-01-01')
            | put(date=date.strftime('time', '%Y/%m/%d'))
            | keep('date')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'date': '2016/01/01'}
        ])
