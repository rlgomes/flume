"""
put proc unittests
"""
import unittest

from robber import expect
from flume import *


class PutTest(unittest.TestCase):

    def test_put_add_a_numerical_field(self):
        results = []
        (
            emit(points=[{}, {}])
            | put(foo=1)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1},
            {'foo': 1}
        ])

    def test_put_add_a_nested_field(self):
        results = []
        (
            emit(points=[{}, {}])
            | put(foo={
                'value': 1
            })
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': {'value': 1}},
            {'foo': {'value': 1}}
        ])

    def test_put_multiple_fields(self):
        results = []
        (
            emit(points=[{}, {}])
            | put(foo=1, fizz='buzz')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1, 'fizz': 'buzz'},
            {'foo': 1, 'fizz': 'buzz'}
        ])

    def test_put_multiple_fields_with_multiple_puts(self):
        results = []
        (
            emit(points=[{}, {}])
            | put(foo=1)
            | put(fizz='buzz')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1, 'fizz': 'buzz'},
            {'foo': 1, 'fizz': 'buzz'}
        ])

    def test_put_field_value_interpolations(self):
        results = []
        (
            emit(limit=3, start='2013-01-01')
            | put(count=count())
            | put(message='this is line #{count}')
            | remove('time', 'count')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'message': 'this is line #1'},
            {'message': 'this is line #2'},
            {'message': 'this is line #3'}
        ])

    def test_put_time_value_interpolations(self):
        results = []
        (
            emit(limit=3, start='2013-01-01')
            | put(count=count())
            | put(message='this happened at "{time}"')
            | remove('time', 'count')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'message': 'this happened at "2013-01-01T00:00:00.000Z"'},
            {'message': 'this happened at "2013-01-01T00:00:01.000Z"'},
            {'message': 'this happened at "2013-01-01T00:00:02.000Z"'}
        ])
