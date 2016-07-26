"""
filter proc unittests
"""
import unittest

from robber import expect
from flume import *


class FilterTest(unittest.TestCase):

    def test_filter_on_a_numerical_field(self):
        results = []
        (
            emit(limit=10, start='2014-01-01', every='1s')
            | put(value=count())
            | filter('value <= 5')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2014-01-01T00:00:00.000Z', 'value': 1},
            {'time': '2014-01-01T00:00:01.000Z', 'value': 2},
            {'time': '2014-01-01T00:00:02.000Z', 'value': 3},
            {'time': '2014-01-01T00:00:03.000Z', 'value': 4},
            {'time': '2014-01-01T00:00:04.000Z', 'value': 5}
        ])

    def test_filter_on_a_string_field(self):
        results = []
        (
            emit(limit=3, start='2014-01-01', every='1s')
            | (put(foo='bar'), put(foo='baz'))
            | filter('foo == "bar"')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2014-01-01T00:00:00.000Z', 'foo': 'bar'},
            {'time': '2014-01-01T00:00:01.000Z', 'foo': 'bar'},
            {'time': '2014-01-01T00:00:02.000Z', 'foo': 'bar'}
        ])

    def test_filter_on_a_boolean_field(self):
        results = []
        (
            emit(limit=3, start='2014-01-01', every='1s')
            | (put(foo=True), put(foo=False))
            | filter('foo')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2014-01-01T00:00:00.000Z', 'foo': True},
            {'time': '2014-01-01T00:00:01.000Z', 'foo': True},
            {'time': '2014-01-01T00:00:02.000Z', 'foo': True}
        ])
