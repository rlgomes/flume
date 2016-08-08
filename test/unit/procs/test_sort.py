"""
remove proc unittests
"""
import unittest

from robber import expect
from flume import *


class SortTest(unittest.TestCase):

    def test_sort_on_invalid_order(self):
        try:
            (
                emit(limit=10, start='2016-01-01', every='1s')
                | put(count=count())
                | sort('count', order='bananas')
            ).execute()

            raise Exception('previous statement should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('order can be "asc" or "desc", not "bananas"')

    def test_sort_limits_exceeded(self):
        try:
            (
                emit(limit=10, start='2016-01-01', every='1s')
                | put(count=count())
                | sort('count', limit=5)
            ).execute()

            raise Exception('previous statement should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('sort buffer overflown, limit is 5, buffering 6')

    def test_sort_with_no_fields_is_idempotent(self):
        results = []
        (
            emit(limit=5, start='2016-01-01', every='1s')
            | put(count=count())
            | sort()
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T00:00:01.000Z', 'count': 2},
            {'time': '2016-01-01T00:00:02.000Z', 'count': 3},
            {'time': '2016-01-01T00:00:03.000Z', 'count': 4},
            {'time': '2016-01-01T00:00:04.000Z', 'count': 5}
        ])

    def test_sort_ascending_on_single_inorder_field(self):
        results = []
        (
            emit(limit=5, start='2016-01-01', every='1s')
            | put(count=count())
            | sort('count', order='asc')
            | memory(results)
        ).execute()

        # time should be removed since its no longer in order
        expect(results).to.eq([
            {'count': 1},
            {'count': 2},
            {'count': 3},
            {'count': 4},
            {'count': 5}
        ])

    def test_sort_descending_on_single_inorder_field(self):
        results = []
        (
            emit(limit=5, start='2016-01-01', every='1s')
            | put(count=count())
            | sort('count', order='desc')
            | memory(results)
        ).execute()

        # time should be removed since its no longer in order
        expect(results).to.eq([
            {'count': 5},
            {'count': 4},
            {'count': 3},
            {'count': 2},
            {'count': 1}
        ])

    def test_sort_ascending_on_multiple_fields(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | put(count=count())
            | (
                put(foo=iterate(['a', 'b'])),
                put(foo=iterate(['b', 'a']))
            ) | sort('foo', 'count', order='asc')
            | memory(results)
        ).execute()

        # time should be removed since its no longer in order
        expect(results).to.eq([
            {'foo': 'a', 'count': 1},
            {'foo': 'a', 'count': 2},
            {'foo': 'a', 'count': 3},
            {'foo': 'b', 'count': 1},
            {'foo': 'b', 'count': 2},
            {'foo': 'b', 'count': 3}
        ])

    def test_sort_descending_on_multiple_fields(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | put(count=count())
            | (
                put(foo=iterate(['a', 'b'])),
                put(foo=iterate(['b', 'a']))
            ) | sort('foo', 'count', order='desc')
            | memory(results)
        ).execute()

        # time should be removed since its no longer in order
        expect(results).to.eq([
            {'foo': 'b', 'count': 3},
            {'foo': 'b', 'count': 2},
            {'foo': 'b', 'count': 1},
            {'foo': 'a', 'count': 3},
            {'foo': 'a', 'count': 2},
            {'foo': 'a', 'count': 1}
        ])
