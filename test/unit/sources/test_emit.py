"""
emit source unittests
"""
import unittest

from robber import expect

from flume import *


class EmitTest(unittest.TestCase):

    def test_emit_no_points(self):
        results = []
        (
            emit(points=[])
            | memory(results)
        ).execute()
        expect(results).to.eq([])

    def test_emit_some_points(self):
        results = []
        data = [{'value': 1}, {'value': 2}, {'value': 3}]
        (
            emit(points=data)
            | memory(results)
        ).execute()
        expect(results).to.eq(data)

    def test_emit_with_limit(self):
        results = []
        (
            emit(limit=10, every='0.01s')
            | memory(results)
        ).execute()
        expect(results).to.have.length(10)

    def test_emit_starting_at_specific_date(self):
        results = []
        (
            emit(start='2015-01-01', limit=5, every='1s')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2015-01-01T00:00:00.000Z'},
            {'time': '2015-01-01T00:00:01.000Z'},
            {'time': '2015-01-01T00:00:02.000Z'},
            {'time': '2015-01-01T00:00:03.000Z'},
            {'time': '2015-01-01T00:00:04.000Z'}
        ])

    def test_emit_with_every_month_expression(self):
        results = []
        (
            emit(start='2015-01-01', limit=5, every='1M')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2015-01-01T00:00:00.000Z'},
            {'time': '2015-02-01T00:00:00.000Z'},
            {'time': '2015-03-01T00:00:00.000Z'},
            {'time': '2015-04-01T00:00:00.000Z'},
            {'time': '2015-05-01T00:00:00.000Z'}
        ])
