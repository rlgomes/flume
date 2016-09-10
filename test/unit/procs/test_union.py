# -*- coding: utf-8 -*-
"""
union proc unittests
"""
import unittest

from robber import expect
from flume import *


def equal_sets(first, second):
    """
    verifies the elements contained in first list are all present in second list
    and vice versa but not verifying the order in anyway
    """
    for element in first:
        expect(second).to.contain(element)

    for element in second:
        expect(first).to.contain(element)

class UnionTest(unittest.TestCase):

    # test basic union properties from
    # https://en.wikipedia.org/wiki/Set_(mathematics)

    def test_idempotency(self):
        """
        A ∪ A = A
        """
        AnA = []

        A = [
            {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
        ]

        (
            (emit(points=A), emit(points=A))
            | union()
            | memory(AnA)
        ).execute()

        expect(AnA).to.eq(A)

    def test_domination(self):
        """
        A ∪ ∅ = A
        """
        An0 = []

        A = [
            {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
        ]

        (
            (emit(points=A), emit(points=[]))
            | union()
            | memory(An0)
        ).execute()

        expect(An0).to.eq(A)

    def test_commutativity(self):
        """
        A ∪ B = B ∪ A
        """
        AuB = []
        BuA = []

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
            | union()
            | memory(AuB)
        ).execute()

        (
            (emit(points=B), emit(points=A))
            | union()
            | memory(BuA)
        ).execute()

        expect(AuB).to.eq(BuA)

    def test_associativity(self):
        """
        A ∪ (B ∪ C) = (A ∪ B) ∪ C.
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
                (emit(points=B), emit(points=C)) | union()
            )
            | union()
            | memory(ABC1)
        ).execute()

        (
            (
                (emit(points=A), emit(points=B)) | union(),
                emit(points=C)
            )
            | union()
            | memory(ABC2)
        ).execute()

        expect(ABC1).to.eq(ABC2)

    def test_idempotency_with_timeless_data(self):
        """
        A ∪ A = A
        """
        AnA = []

        A = [
            {'foo': '1', 'a': 0},
            {'foo': '2', 'a': 1},
            {'foo': '3', 'a': 2}
        ]

        (
            (emit(points=A), emit(points=A))
            | union('foo')
            | memory(AnA)
        ).execute()

        expect(AnA).to.eq(A)

    def test_domination_with_timeless_data(self):
        """
        A ∪ ∅ = A
        """
        An0 = []

        A = [
            {'foo': 1, 'a': 0},
            {'foo': 2, 'a': 1},
            {'foo': 3, 'a': 2}
        ]

        (
            (emit(points=A), emit(points=[]))
            | union('foo')
            | memory(An0)
        ).execute()

        expect(An0).to.eq(A)

    def test_commutativity_with_timeless_data(self):
        """
        A ∪ B = B ∪ A
        """
        AuB = []
        BuA = []

        A = [
            {'foo': '0', 'a': 0},
            {'foo': '1', 'a': 1},
            {'foo': '2', 'a': 2}
        ]
        B = [
            {'foo': '1', 'a': 1},
            {'foo': '3', 'a': 2},
            {'foo': '5', 'a': 3}
        ]

        (
            (emit(points=A), emit(points=B))
            | union('foo')
            | memory(AuB)
        ).execute()

        (
            (emit(points=B), emit(points=A))
            | union('foo')
            | memory(BuA)
        ).execute()

        # timeless data has no order
        equal_sets(AuB, BuA)

    def test_associativity_with_timeless_data(self):
        """
        A ∪ (B ∪ C) = (A ∪ B) ∪ C.
        """
        ABC1 = []
        ABC2 = []

        A = [
            {'foo': '0', 'a': 0},
            {'foo': '1', 'a': 1},
            {'foo': '2', 'a': 2}
        ]
        B = [
            {'foo': '1', 'a': 1},
            {'foo': '3', 'a': 2},
            {'foo': '5', 'a': 3}
        ]
        C = [
            {'foo': '2', 'a': 3},
            {'foo': '4', 'a': 4},
            {'foo': '6', 'a': 5}
        ]

        (
            (
                emit(points=A),
                (emit(points=B), emit(points=C)) | union('foo')
            )
            | union('foo')
            | memory(ABC1)
        ).execute()

        (
            (
                (emit(points=A), emit(points=B)) | union('foo'),
                emit(points=C)
            )
            | union('foo')
            | memory(ABC2)
        ).execute()

        equal_sets(ABC1, ABC2)

    def test_single_historical_stream(self):
        results = []
        (
            emit(limit=3, start='2000-01-01')
            | union()
            | memory(results)
        ).execute()
        expect(results).to.have.length(3)

    def test_single_live_stream(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | union()
            | memory(results)
        ).execute()
        expect(results).to.have.length(3)

    def test_empty_to_union_of_a_single_historical_stream(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | ()
            | union()
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z'},
            {'time': '2016-01-01T00:00:01.000Z'},
            {'time': '2016-01-01T00:00:02.000Z'}
        ])

    def test_empty_to_union_of_a_single_live_stream(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | ()
            | union()
            | memory(results)
        ).execute()
        expect(results).to.have.length(3)

    def test_union_two_historical_streams(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | (
                put(foo='bar'),
                put(fizz='buzz')
            ) | union()
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'foo': 'bar', 'fizz': 'buzz'},
            {'time': '2016-01-01T00:00:01.000Z', 'foo': 'bar', 'fizz': 'buzz'},
            {'time': '2016-01-01T00:00:02.000Z', 'foo': 'bar', 'fizz': 'buzz'}
        ])

    def test_union_two_live_streams(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | (
                put(foo='bar'),
                put(fizz='buzz')
            ) | union()
            | memory(results)
        ).execute()
        expect(results).to.have.length(3)

    def test_union_on_a_non_time_field(self):
        results = []
        (
            (
                emit(points=[
                    {'foo': 1, 'bar': 'baz'},
                    {'foo': 2, 'bar': 'baz'}
                ]),
                emit(points=[
                    {'foo': 1, 'baz': 'bar'},
                    {'foo': 3, 'baz': 'bar'}
                ])
            )
            | union('foo')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'foo': 1, 'bar': 'baz', 'baz': 'bar'},
            {'foo': 2, 'bar': 'baz'},
            {'foo': 3, 'baz': 'bar'}
        ])

    def test_union_on_multiple_fields(self):
        results = []
        (
            (
                emit(points=[
                    {'foo': 1, 'bar': 'a', 'color': 'green'},
                    {'foo': 2, 'bar': 'b', 'color': 'blue'},
                    {'foo': 3, 'bar': 'b', 'color': 'blue'},
                ]),
                emit(points=[
                    {'foo': 2, 'bar': 'b', 'shape': 'circle'},
                    {'foo': 1, 'bar': 'a', 'shape': 'square'},
                ])
            )
            | union('foo', 'bar')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1, 'bar': 'a', 'color': 'green', 'shape': 'square'},
            {'foo': 2, 'bar': 'b', 'color': 'blue', 'shape': 'circle'},
            {'foo': 3, 'bar': 'b', 'color': 'blue'}
        ])
