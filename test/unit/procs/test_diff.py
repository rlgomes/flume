# -*- coding: utf-8 -*-
"""
diff proc unittests
"""
import unittest

from robber import expect
from flume import *


class DiffTest(unittest.TestCase):

    # test basic intersection properties from
    # https://en.wikipedia.org/wiki/Set_(mathematics)

    def test_empty_set(self):
        """
        A △ A = ∅
        """
        AnA = []

        A = [
            {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
        ]

        (
            (emit(points=A), emit(points=A))
            | diff()
            | memory(AnA)
        ).execute()

        expect(AnA).to.eq([])

    def test_neutral(self):
        """
        A △ ∅ = ∅ """
        An0 = []

        A = [
            {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
            {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
            {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
        ]

        (
            (emit(points=A), emit(points=[]))
            | diff()
            | memory(An0)
        ).execute()

        expect(An0).to.eq(A)

    def test_commutativity(self):
        """
        A △ B =  B △ A
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
            | diff()
            | memory(AnB)
        ).execute()

        (
            (emit(points=B), emit(points=A))
            | diff()
            | memory(BnA)
        ).execute()

        expect(AnB).to.eq(BnA)

    def test_associativity(self):
        """
        A △ (B △ C) = (A △ B) △ C.
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
                (emit(points=B), emit(points=C)) | diff()
            )
            | diff()
            | memory(ABC1)
        ).execute()

        (
            (
                (emit(points=A), emit(points=B)) | diff(),
                emit(points=C)
            )
            | diff()
            | memory(ABC2)
        ).execute()

        expect(ABC1).to.eq(ABC2)

    def test_empty_to_diff_of_a_single_historical_stream(self):
        results = []
        (
            emit(limit=3, start='2016-01-01', every='1s')
            | ()
            | diff()
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z'},
            {'time': '2016-01-01T00:00:01.000Z'},
            {'time': '2016-01-01T00:00:02.000Z'}
        ])

    def test_diff_of_a_single_historical_stream(self):
        results = []
        (
            emit(limit=3, start='2000-01-01')
            | diff()
            | memory(results)
        ).execute()

        expect(results).to.have.length(3)

    def test_diff_of_a_single_live_stream(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | diff()
            | memory(results)
        ).execute()

        expect(results).to.have.length(3)

    def test_empty_to_diff_of_a_single_live_stream(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | ()
            | diff()
            | memory(results)
        ).execute()

        expect(results).to.have.length(3)

    def test_diff_two_historical_streams(self):
        results = []
        (
            (
                emit(limit=5, start='2016-01-01T00:00:00.000Z', every='1s')
                | put(foo='bar'),
                emit(limit=3, start='2016-01-01T00:00:01.000Z', every='1s')
                | put(fizz='buzz'),
            )
            | diff()
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'foo': 'bar'},
            {'time': '2016-01-01T00:00:04.000Z', 'foo': 'bar'}
        ])

    def test_intersect_two_live_streams(self):
        results = []
        (
            (
                emit(limit=2, start='1s ago', every='1s')
                | put(foo='bar'),
                emit(limit=1, start='0s ago', every='1s')
                | put(fizz='buzz'),
            )
            | diff()
            | remove('time')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'foo': 'bar'}
        ])

    def test_diff_on_a_non_time_field(self):
        results = []
        (
            (
                emit(points=[
                    {'foo': 1, 'bar': 'baz'},
                    {'foo': 2, 'bar': 'baz'},
                    {'foo': 3, 'bar': 'baz'}
                ]),
                emit(points=[
                    {'foo': 0, 'baz': 'bar'},
                    {'foo': 2, 'baz': 'bar'},
                    {'foo': 3, 'baz': 'bar'}
                ])
            )
            | diff('foo')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'foo': 1, 'bar': 'baz'},
            {'foo': 0, 'baz': 'bar'}
        ])

    def test_diff_on_multiple_fields(self):
        results = []
        (
            (
                emit(points=[
                    {'foo': 1, 'bar': 'a', 'color': 'green'},
                    {'foo': 2, 'bar': 'b', 'color': 'blue'},
                ]),
                emit(points=[
                    {'foo': 2, 'bar': 'b', 'shape': 'circle'},
                    {'foo': 1, 'bar': 'b', 'shape': 'square'},
                ])
            )
            | diff('foo', 'bar')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'foo': 1, 'bar': 'a', 'color': 'green'},
            {'foo': 1, 'bar': 'b', 'shape': 'square'}
        ])
