"""
keep proc unittests
"""
import unittest

from robber import expect
from flume import *


class KeepTest(unittest.TestCase):

    def test_keep_a_numerical_field(self):
        results = []
        (
            emit(limit=3, every='0.01s')
            | put(value=count())
            | keep('value')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'value': 1},
            {'value': 2},
            {'value': 3}
        ])

    def test_keep_time_field(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | put(value=count(), foo='bar')
            | keep('time')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z'},
            {'time': '2016-01-01T00:00:01.000Z'},
            {'time': '2016-01-01T00:00:02.000Z'}
        ])

    def test_keep_multiple_fields(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | put(value=count(), foo='bar')
            | keep('time', 'value', 'foo')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'foo': 'bar', 'value': 1},
            {'time': '2016-01-01T00:00:01.000Z', 'foo': 'bar', 'value': 2},
            {'time': '2016-01-01T00:00:02.000Z', 'foo': 'bar', 'value': 3}
        ])
