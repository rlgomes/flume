"""
seq proc unittests
"""
import unittest

from robber import expect
from flume import *


class SeqTest(unittest.TestCase):

    def test_seq_can_chain_two_historical_streams(self):
        results = []
        (
            seq(emit(limit=3, start='2016-01-01T00:00:00.000Z'),
                emit(limit=3, start='2016-01-01T00:00:03.000Z'))
            | put(value=count())
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'value': 1},
            {'time': '2016-01-01T00:00:01.000Z', 'value': 2},
            {'time': '2016-01-01T00:00:02.000Z', 'value': 3},
            {'time': '2016-01-01T00:00:03.000Z', 'value': 4},
            {'time': '2016-01-01T00:00:04.000Z', 'value': 5},
            {'time': '2016-01-01T00:00:05.000Z', 'value': 6}
        ])


    def test_seq_can_chain_two_live_streams(self):
        results = []
        (
            seq(emit(limit=3, every='0.1s'),
                emit(limit=3, every='0.1s'))
            | reduce(count=count())
            | keep('count')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'count': 6}
        ])
