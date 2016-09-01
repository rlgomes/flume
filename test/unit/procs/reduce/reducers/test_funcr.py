"""
funcr reducer unittests
"""
import unittest

from datetime import datetime

from robber import expect
from flume import *


class FuncrReducerTest(unittest.TestCase):

    def test_funcr_with_lambda(self):
        results = []
        (
            emit(limit=5, start='2016-01-01')
            | put(count=count())
            | put(count=funcr(lambda value: value/10.0)('count'))
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'count': 0.1},
            {'time': '2016-01-01T00:00:01.000Z', 'count': 0.2},
            {'time': '2016-01-01T00:00:02.000Z', 'count': 0.3},
            {'time': '2016-01-01T00:00:03.000Z', 'count': 0.4},
            {'time': '2016-01-01T00:00:04.000Z', 'count': 0.5}
        ])

    def test_funcr_with_function(self):
        def plus_one(value):
            return value + 1

        results = []
        (
            emit(limit=5, start='2016-01-01')
            | put(count=count())
            | put(count=funcr(plus_one)('count'))
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'count': 2},
            {'time': '2016-01-01T00:00:01.000Z', 'count': 3},
            {'time': '2016-01-01T00:00:02.000Z', 'count': 4},
            {'time': '2016-01-01T00:00:03.000Z', 'count': 5},
            {'time': '2016-01-01T00:00:04.000Z', 'count': 6}
        ])
