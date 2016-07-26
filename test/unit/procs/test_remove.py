"""
remove proc unittests
"""
import unittest

from robber import expect
from flume import *


class RemoveTest(unittest.TestCase):

    def test_remove_a_numerical_field(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | put(value=count(), foo='bar')
            | remove('value')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'foo': 'bar'},
            {'time': '2016-01-01T00:00:01.000Z', 'foo': 'bar'},
            {'time': '2016-01-01T00:00:02.000Z', 'foo': 'bar'}
        ])

    def test_remove_time_field(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | put(value=count())
            | remove('time')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'value': 1},
            {'value': 2},
            {'value': 3}
        ])

    def test_remove_multiple_fields(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | put(value=count(), foo='bar')
            | remove('time', 'value', 'foo')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {},
            {},
            {}
        ])
