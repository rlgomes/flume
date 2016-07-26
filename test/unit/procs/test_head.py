"""
head proc unittests
"""
import unittest

from robber import expect
from flume import *


class HeadTest(unittest.TestCase):

    def test_head_on_empty_stream_works(self):
        results = []
        (
            emit(points=[])
            | head(3)
            | memory(results)
        ).execute()
        expect(results).to.eq([])

    def test_head_on_stream_with_less_than_N_elements(self):
        results = []
        (
            emit(points=[
                {'foo': 1},
                {'foo': 2},
                {'foo': 3}
            ])
            | head(5)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1},
            {'foo': 2},
            {'foo': 3}
        ])

    def test_head_on_stream_with_more_than_N_elements(self):
        results = []
        (
            emit(points=[
                {'foo': 1},
                {'foo': 2},
                {'foo': 3},
                {'foo': 4},
                {'foo': 5}
            ])
            | head(3)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1},
            {'foo': 2},
            {'foo': 3}
        ])
