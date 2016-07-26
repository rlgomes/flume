# -*- coding: utf-8 -*-
"""
intersect proc unittests
"""
import unittest

from robber import expect
from flume import *


class IntersectTest(unittest.TestCase):

    # test basic intersection properties from
    # https://en.wikipedia.org/wiki/Set_(mathematics)

    def test_idempotency(self):
        """
        A ∩ A = A
        """
        AnA = []

        A = [
            {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
        ]

        (
            (emit(points=A), emit(points=A))
            | intersect()
            | memory(AnA)
        ).execute()

        expect(AnA).to.eq(A)

    def test_domination(self):
        """
        A ∩ ∅ = ∅
        """
        An0 = []

        A = [
            {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
        ]

        (
            (emit(points=A), emit(points=[]))
            | intersect()
            | memory(An0)
        ).execute()

        expect(An0).to.eq([])

    def test_commutativity(self):
        """
        A ∩ B = B ∩ A
        """
        AnB = []
        BnA = []

        A = [
            {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
        ]
        B = [
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:03:00.000Z', 'a': 2},
            {'time': '2010-01-01T00:05:00.000Z', 'a': 3}
        ]

        (
            (emit(points=A), emit(points=B))
            | intersect()
            | memory(AnB)
        ).execute()

        (
            (emit(points=B), emit(points=A))
            | intersect()
            | memory(BnA)
        ).execute()

        expect(AnB).to.eq(BnA)

    def test_associativity(self):
        """
        A ∩ (B ∩ C) = (A ∩ B) ∩ C.
        """
        ABC1 = []
        ABC2 = []

        A = [
            {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
        ]
        B = [
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:03:00.000Z', 'a': 2},
            {'time': '2010-01-01T00:05:00.000Z', 'a': 3}
        ]
        C = [
            {'time': '2010-01-01T00:02:00.000Z', 'a': 3},
            {'time': '2010-01-01T00:04:00.000Z', 'a': 4},
            {'time': '2010-01-01T00:06:00.000Z', 'a': 5}
        ]

        (
            (
                emit(points=A),
                (emit(points=B), emit(points=C)) | intersect()
            )
            | intersect()
            | memory(ABC1)
        ).execute()

        (
            (
                (emit(points=A), emit(points=B)) | intersect(),
                emit(points=C)
            )
            | intersect()
            | memory(ABC2)
        ).execute()

        expect(ABC1).to.eq(ABC2)

    def test_empty_to_intersect_of_a_single_historical_stream(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | ()
            | intersect()
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z'},
            {'time': '2016-01-01T00:00:01.000Z'},
            {'time': '2016-01-01T00:00:02.000Z'}
        ])

    def test_single_historical_stream(self):
        results = []
        (
            emit(limit=3, start='2000-01-01')
            | intersect()
            | memory(results)
        ).execute()
        expect(results).to.have.length(3)

    def test_single_live_stream(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | intersect()
            | memory(results)
        ).execute()
        expect(results).to.have.length(3)


    def test_empty_to_intersect_of_a_single_live_stream(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | ()
            | intersect()
            | memory(results)
        ).execute()
        expect(results).to.have.length(3)

    def test_intersect_two_historical_streams(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | (
                put(foo='bar'),
                put(fizz='buzz')
            ) | intersect()
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'foo': 'bar', 'fizz': 'buzz'},
            {'time': '2016-01-01T00:00:01.000Z', 'foo': 'bar', 'fizz': 'buzz'},
            {'time': '2016-01-01T00:00:02.000Z', 'foo': 'bar', 'fizz': 'buzz'}
        ])

    def test_intersect_two_live_streams(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | (
                put(foo='bar'),
                put(fizz='buzz')
            ) | intersect()
            | memory(results)
        ).execute()
        expect(results).to.have.length(3)

    def test_intersect_on_a_non_time_field(self):
        results = []
        (
            ([
                emit(points=[
                    {'foo': 1, 'bar': 'baz'},
                    {'foo': 2, 'bar': 'baz'},
                    {'foo': 3, 'bar': 'baz'}
                ]),
                emit(points=[
                    {'foo': 1, 'baz': 'bar'},
                    {'foo': 2, 'baz': 'bar'},
                    {'foo': 3, 'baz': 'bar'}
                ])
            ])
            | intersect('foo')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1, 'bar': 'baz', 'baz': 'bar'},
            {'foo': 2, 'bar': 'baz', 'baz': 'bar'},
            {'foo': 3, 'bar': 'baz', 'baz': 'bar'}
        ])

    def test_intersect_on_multiple_fields(self):
        results = []
        (
            ([
                emit(points=[
                    {'foo': 1, 'bar': 'a', 'color': 'green'},
                    {'foo': 2, 'bar': 'b', 'color': 'blue'},
                ]),
                emit(points=[
                    {'foo': 2, 'bar': 'b', 'shape': 'circle'},
                    {'foo': 1, 'bar': 'a', 'shape': 'square'},
                ])
            ])
            | intersect('foo', 'bar')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1, 'bar': 'a', 'color': 'green', 'shape': 'square'},
            {'foo': 2, 'bar': 'b', 'color': 'blue', 'shape': 'circle'}
        ])
