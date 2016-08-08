"""
reduce proc unittests
"""
import unittest

from robber import expect
from flume import *


class ReduceTest(unittest.TestCase):

    def test_reduce_to_a_static_value(self):
        results = []
        (
            emit(limit=5, every='0.001s')
            | reduce(count=0)
            | keep('count')
            | memory(results)
        ).execute()
        expect(results).to.eq([{'count': 0}])

    def test_reduce_field_with_interpolated_field_value(self):
        results = []
        (
            emit(limit=5, every='0.001s')
            | put(count=count())
            | reduce(message='count is {count}')
            | keep('message')
            | memory(results)
        ).execute()
        expect(results).to.eq([{'message': 'count is 5'}])

    def test_reduce_field_with_interpolated_time_value(self):
        results = []
        (
            emit(limit=5, start='2016-01-01')
            | reduce(message='last point at "{time}"')
            | keep('message')
            | memory(results)
        ).execute()
        expect(results).to.eq([{'message': 'last point at "2016-01-01T00:00:04.000Z"'}])

    def test_reduce_to_a_count(self):
        results = []
        (
            emit(limit=5, every='0.001s')
            | reduce(count=count())
            | keep('count')
            | memory(results)
        ).execute()
        expect(results).to.eq([{'count': 5}])

    def test_reduce_to_the_maximum(self):
        results = []
        (
            emit(limit=5, every='0.001s')
            | put(count=count())
            | reduce(maximum=maximum('count'))
            | keep('maximum')
            | memory(results)
        ).execute()
        expect(results).to.eq([{'maximum': 5}])

    def test_reduce_to_the_minimum(self):
        results = []
        (
            emit(limit=5, every='0.001s')
            | put(count=count())
            | reduce(minimum=minimum('count'))
            | keep('minimum')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'minimum': 1}])

    def test_reduce_with_custom_reducer(self):

        class count_odds(reducer):

            def __init__(self, fieldname):
                self.count = 0
                self.fieldname = fieldname

            def update(self, point):
                if self.fieldname in point:
                    if point[self.fieldname] % 2 != 0:
                        self.count += 1

            def result(self):
                return self.count

            def reset(self):
                self.count = 0

        results = []
        (
            emit(limit=10, every='0.001s')
            | put(count=count())
            | reduce(odds=count_odds('count'))
            | keep('odds')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'odds': 5}])

    def test_reduce_with_mixed_fields(self):
        results = []
        (
            emit(limit=10, every='0.001s')
            | reduce(count=count(), foo='bar', someid=1)
            | keep('count', 'foo', 'someid')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'count': 10, 'foo': 'bar', 'someid': 1}
        ])

    def test_reduce_to_a_count_by_a_field(self):
        results = []
        (
            emit(limit=10, every='0.001s')
            | (
                put(foo='bar'),
                put(foo='baz')
            ) | reduce(count=count(), by=['foo'])
            | keep('foo', 'count')
            | memory(results)
        ).execute()

        expect(results).to.have.length(2)
        expect(results).to.contain({'foo': 'bar', 'count': 10})
        expect(results).to.contain({'foo': 'baz', 'count': 10})

    def test_reduce_to_a_maximum_by_a_field(self):
        results = []
        (
            emit(limit=10, every='0.001s')
            | put(count=count())
            | (
                put(foo='bar'),
                put(foo='baz')
            ) | reduce(maximum=maximum('count'), by=['foo'])
            | keep('foo', 'maximum')
            | memory(results)
        ).execute()
        expect(results).to.have.length(2)
        expect(results).to.contain({'foo': 'bar', 'maximum': 10})
        expect(results).to.contain({'foo': 'baz', 'maximum': 10})

    def test_reduce_to_a_minimum_by_a_field(self):
        results = []
        (
            emit(limit=10, every='0.001s')
            | put(count=count())
            | (
                put(foo='bar'),
                put(foo='baz')
            ) | reduce(minimum=minimum('count'), by=['foo'])
            | keep('foo', 'minimum')
            | memory(results)
        ).execute()
        expect(results).to.have.length(2)
        expect(results).to.contain({'foo': 'bar', 'minimum': 1})
        expect(results).to.contain({'foo': 'baz', 'minimum': 1})

    def test_reduce_to_a_count_by_multiple_fields(self):
        results = []
        (
            emit(limit=10, every='0.001s')
            | (
                put(a=iterate([2]), b=iterate([2])),
                put(a=iterate([2, 3]), b=iterate([1, 2]))
            ) | reduce(count=count(), by=['a', 'b'])
            | keep('a', 'b', 'count')
            | memory(results)
        ).execute()

        expect(results).to.have.length(3)
        expect(results).to.contain({'a': 2, 'b': 2, 'count': 10})
        expect(results).to.contain({'a': 2, 'b': 1, 'count': 5})
        expect(results).to.contain({'a': 3, 'b': 2, 'count': 5})

    def test_reduce_with_mixed_fields_by_a_field(self):
        results = []
        (
            emit(limit=10, every='0.001s')
            | (
                put(foo='bar'),
                put(foo='baz')
            ) | reduce(count=count(), fizz='buzz', someid=1, by=['foo'])
            | keep('fizz', 'someid', 'foo', 'count')
            | memory(results)
        ).execute()

        expect(results).to.have.length(2)
        expect(results).to.contain({
            'fizz': 'buzz',
            'someid': 1,
            'foo': 'bar',
            'count': 10
        })

        expect(results).to.contain({
            'fizz': 'buzz',
            'someid': 1,
            'foo': 'baz',
            'count': 10
        })

    def test_reduce_every_count(self):
        results = []
        (
            emit(limit=10, every='1s', start='2016-01-01')
            | reduce(count=count(), every='3s')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'count': 3},
            {'time': '2016-01-01T00:00:03.000Z', 'count': 3},
            {'time': '2016-01-01T00:00:06.000Z', 'count': 3},
            {'time': '2016-01-01T00:00:09.000Z', 'count': 1}
        ])

    def test_reduce_every_maximum(self):
        results = []
        (
            emit(limit=10, every='1s', start='2016-01-01')
            | put(count=count())
            | reduce(maximum=maximum('count'), every='3s')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'maximum': 3},
            {'time': '2016-01-01T00:00:03.000Z', 'maximum': 6},
            {'time': '2016-01-01T00:00:06.000Z', 'maximum': 9},
            {'time': '2016-01-01T00:00:09.000Z', 'maximum': 10}
        ])

    def test_reduce_every_minimum(self):
        results = []
        (
            emit(limit=10, every='1s', start='2016-01-01')
            | put(count=count())
            | reduce(minimum=minimum('count'), every='3s')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'minimum': 1},
            {'time': '2016-01-01T00:00:03.000Z', 'minimum': 4},
            {'time': '2016-01-01T00:00:06.000Z', 'minimum': 7},
            {'time': '2016-01-01T00:00:09.000Z', 'minimum': 10}
        ])

    def test_reduce_every_count_with_mixed_fields(self):
        results = []
        (
            emit(limit=10, every='1s', start='2016-01-01')
            | reduce(count=count(), foo='bar', someid=1, every='3s')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {
                'time': '2016-01-01T00:00:00.000Z',
                'count': 3,
                'foo': 'bar',
                'someid': 1
            },
            {
                'time': '2016-01-01T00:00:03.000Z',
                'count': 3,
                'foo': 'bar',
                'someid': 1
            },
            {
                'time': '2016-01-01T00:00:06.000Z',
                'count': 3,
                'foo': 'bar',
                'someid': 1
            },
            {
                'time': '2016-01-01T00:00:09.000Z',
                'count': 1,
                'foo': 'bar',
                'someid': 1
            }
        ])

    def test_reduce_every_count_by_a_field(self):
        results = []
        (
            emit(limit=10, start='2016-01-01', every='1s')
            | (
                put(foo='bar'),
                put(foo='baz')
            ) | reduce(count=count(), every='2s', by=['foo'])
            | memory(results)
        ).execute()
        expect(results).to.have.length(10)

        for point in [
                {'time': '2016-01-01T00:00:00.000Z', 'foo': 'bar', 'count': 2},
                {'time': '2016-01-01T00:00:00.000Z', 'foo': 'baz', 'count': 2},
                {'time': '2016-01-01T00:00:02.000Z', 'foo': 'bar', 'count': 2},
                {'time': '2016-01-01T00:00:02.000Z', 'foo': 'baz', 'count': 2},
                {'time': '2016-01-01T00:00:04.000Z', 'foo': 'bar', 'count': 2},
                {'time': '2016-01-01T00:00:04.000Z', 'foo': 'baz', 'count': 2},
                {'time': '2016-01-01T00:00:06.000Z', 'foo': 'bar', 'count': 2},
                {'time': '2016-01-01T00:00:06.000Z', 'foo': 'baz', 'count': 2},
                {'time': '2016-01-01T00:00:08.000Z', 'foo': 'bar', 'count': 2},
                {'time': '2016-01-01T00:00:08.000Z', 'foo': 'baz', 'count': 2}]:
            expect(results).to.contain(point)

    def test_reduce_every_with_no_reset(self):
        results = []
        (
            emit(limit=10, every='1s', start='2016-01-01')
            | reduce(count=count(), every='3s', reset=False)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'count': 3},
            {'time': '2016-01-01T00:00:03.000Z', 'count': 6},
            {'time': '2016-01-01T00:00:06.000Z', 'count': 9},
            {'time': '2016-01-01T00:00:09.000Z', 'count': 10}
        ])

    def test_reduce_every_with_no_reset_by_a_field(self):
        results = []
        (
            emit(limit=9, every='1s', start='2016-01-01')
            | (
                put(foo='bar'),
                put(foo='baz')
            ) | reduce(count=count(), every='3s', by=['foo'], reset=False)
            | memory(results)
        ).execute()
        expect(results).to.have.length(6)

        for point in [
                {'time': '2016-01-01T00:00:00.000Z', 'count': 3, 'foo': 'bar'},
                {'time': '2016-01-01T00:00:03.000Z', 'count': 6, 'foo': 'bar'},
                {'time': '2016-01-01T00:00:06.000Z', 'count': 9, 'foo': 'bar'},
                {'time': '2016-01-01T00:00:00.000Z', 'count': 3, 'foo': 'baz'},
                {'time': '2016-01-01T00:00:03.000Z', 'count': 6, 'foo': 'baz'},
                {'time': '2016-01-01T00:00:06.000Z', 'count': 9, 'foo': 'baz'}]:
            expect(results).to.contain(point)

    def test_reduce_with_timeless_points(self):
        results = []
        (
            emit(limit=10, every='1s', start='2016-01-01')
            | remove('time')
            | reduce(count=count())
            | memory(results)
        ).execute()
        expect(results).to.eq([{'count': 10}])

    def test_reduce_monthly_day_counts(self):
        results = []
        (
            emit(limit=365, start='2015-01-01', every='1d')
            | reduce(count=count(), every='1 month')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2015-01-01T00:00:00.000Z', 'count': 31},
            {'time': '2015-02-01T00:00:00.000Z', 'count': 28},
            {'time': '2015-03-01T00:00:00.000Z', 'count': 31},
            {'time': '2015-04-01T00:00:00.000Z', 'count': 30},
            {'time': '2015-05-01T00:00:00.000Z', 'count': 31},
            {'time': '2015-06-01T00:00:00.000Z', 'count': 30},
            {'time': '2015-07-01T00:00:00.000Z', 'count': 31},
            {'time': '2015-08-01T00:00:00.000Z', 'count': 31},
            {'time': '2015-09-01T00:00:00.000Z', 'count': 30},
            {'time': '2015-10-01T00:00:00.000Z', 'count': 31},
            {'time': '2015-11-01T00:00:00.000Z', 'count': 30},
            {'time': '2015-12-01T00:00:00.000Z', 'count': 31},
        ])

    def test_reduce_yearl_day_counts(self):
        results = []
        (
            emit(limit=365 * 8 + 2, start='2000-01-01', every='1d')
            | reduce(days=count(), every='1 year')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2000-01-01T00:00:00.000Z', 'days': 366},
            {'time': '2001-01-01T00:00:00.000Z', 'days': 365},
            {'time': '2002-01-01T00:00:00.000Z', 'days': 365},
            {'time': '2003-01-01T00:00:00.000Z', 'days': 365},
            {'time': '2004-01-01T00:00:00.000Z', 'days': 366},
            {'time': '2005-01-01T00:00:00.000Z', 'days': 365},
            {'time': '2006-01-01T00:00:00.000Z', 'days': 365},
            {'time': '2007-01-01T00:00:00.000Z', 'days': 365}
        ])

    def test_reduce_with_single_empty_every_interval(self):
        results = []
        (
            emit(points=[
                {'time': '2016-01-01T00:00:00.000Z', 'value': 1},
                {'time': '2016-01-01T01:00:00.000Z', 'value': 2},
                {'time': '2016-01-01T02:00:00.000Z', 'value': 3},
                {'time': '2016-01-01T04:00:00.000Z', 'value': 4},
                {'time': '2016-01-01T05:00:00.000Z', 'value': 5},
            ])
            | reduce(count=count(), every='1h')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T01:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T02:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T03:00:00.000Z', 'count': 0},
            {'time': '2016-01-01T04:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T05:00:00.000Z', 'count': 1},
        ])

    def test_reduce_with_multiple_empty_every_interval(self):
        results = []
        (
            emit(points=[
                {'time': '2016-01-01T00:00:00.000Z'},
                {'time': '2016-01-01T01:00:00.000Z'},
                {'time': '2016-01-01T02:00:00.000Z'},
                {'time': '2016-01-01T05:00:00.000Z'},
                {'time': '2016-01-01T06:00:00.000Z'},
                {'time': '2016-01-01T09:00:00.000Z'},
                {'time': '2016-01-01T10:00:00.000Z'}
            ])
            | reduce(count=count(), every='1h')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T01:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T02:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T03:00:00.000Z', 'count': 0},
            {'time': '2016-01-01T04:00:00.000Z', 'count': 0},
            {'time': '2016-01-01T05:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T06:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T07:00:00.000Z', 'count': 0},
            {'time': '2016-01-01T08:00:00.000Z', 'count': 0},
            {'time': '2016-01-01T09:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T10:00:00.000Z', 'count': 1}
        ])

    def test_reduce_by_a_nested_field(self):
        results = []
        (
            emit(points=[
                {'time': '2016-01-01T00:00:00.000Z', 'author': {'name': 'joe'}},
                {'time': '2016-01-01T00:01:00.000Z', 'author': {'name': 'joe'}},
                {'time': '2016-01-01T00:02:00.000Z', 'author': {'name': 'bob'}},
                {'time': '2016-01-01T00:03:00.000Z', 'author': {'name': 'joe'}},
                {'time': '2016-01-01T00:03:00.000Z', 'author': {'name': 'bob'}},
            ])
            | reduce(count=count(), by=['author.name'])
            | memory(results)
        ).execute()
        expect(results).to.contain({
            'time': '2016-01-01T00:00:00.000Z',
            'author': {
                'name': 'bob'
            },
            'count': 2
        })
        expect(results).to.contain({
            'time': '2016-01-01T00:00:00.000Z',
            'author': {
                'name': 'joe'
            },
            'count': 3
        })

    def test_reduce_maximum_on_nested_field(self):
        results = []
        (
            emit(points=[
                {'time': '2016-01-01T00:00:00.000Z', 'nested': {'value': 1}},
                {'time': '2016-01-01T00:01:00.000Z', 'nested': {'value': 5}},
                {'time': '2016-01-01T00:02:00.000Z', 'nested': {'value': 3}},
                {'time': '2016-01-01T00:03:00.000Z', 'nested': {'value': 2}},
                {'time': '2016-01-01T00:03:00.000Z', 'nested': {'value': 7}},
            ])
            | reduce(maximum=maximum('nested.value'))
            | remove('time')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'maximum': 7}
        ])
