"""
http adapter unittests
"""

import json
import sys
import unittest

import mock

from StringIO import StringIO
from robber import expect

from flume import *


class StdioTest(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        # make sure to set the stdin/stdout hooks in stdio back to the
        # right values
        stdio.stdin = sys.stdin
        stdio.stdout = sys.stdout

    def test_stdio_can_read_from_empty(self):
        stdio.stdin = StringIO('')
        results = []

        (
            read('stdio')
            | memory(results)
        ).execute()
        expect(results).to.eq([])

    def test_stdio_can_read_a_single_point_(self):
        stdio.stdin = StringIO('{"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}')
        results = []

        (
            read('stdio', format='jsonl')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}
        ])

    def test_stdio_can_read_multiple_points(self):
        stdio.stdin = StringIO('{"time": "2016-01-01T00:00:00.000Z", "foo": 1}\n' +
                               '{"time": "2016-01-01T00:01:00.000Z", "foo": 2}\n' +
                               '{"time": "2016-01-01T00:02:00.000Z", "foo": 3}\n')

        results = []

        (
            read('stdio', format='jsonl')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": 1},
            {"time": "2016-01-01T00:01:00.000Z", "foo": 2},
            {"time": "2016-01-01T00:02:00.000Z", "foo": 3}
        ])
    
    @mock.patch('flume.logger.warn')
    def test_stdio_can_read_a_single_timeless_point_(self, mock_warn):
        stdio.stdin = StringIO('{"foo": "bar"}')
        results = []

        (
            read('stdio', format='jsonl')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"foo": "bar"}
        ])
        expect(mock_warn.call_args).to.eq(mock.call('point missing time field "time"'))

    @mock.patch('flume.logger.warn')
    def test_stdio_can_read_multiple_timeless_points(self, mock_warn):
        stdio.stdin = StringIO('{"foo": 1}\n{"foo": 2}\n{"foo": 3}\n')
        results = []

        (
            read('stdio', format='jsonl')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"foo": 1},
            {"foo": 2},
            {"foo": 3}
        ])
        expect(mock_warn.call_args_list).to.eq([
            mock.call('point missing time field "time"'),
            mock.call('point missing time field "time"'),
            mock.call('point missing time field "time"')
        ])

    def test_stdio_can_read_multiple_points_with_custom_timefield(self):
        stdio.stdin = StringIO('{"bar": "2016-01-01T00:00:00.000Z", "foo": 1}\n' +
                               '{"bar": "2016-01-01T00:01:00.000Z", "foo": 2}\n' +
                               '{"bar": "2016-01-01T00:02:00.000Z", "foo": 3}\n')

        results = []

        (
            read('stdio', format='jsonl', time='bar')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": 1},
            {"time": "2016-01-01T00:01:00.000Z", "foo": 2},
            {"time": "2016-01-01T00:02:00.000Z", "foo": 3}
        ])

    def test_stdio_can_write_nothing(self):
        stdio.stdin = StringIO('')
        stdio.stdout = StringIO('')
        (
            read('stdio')
            | write('stdio')
        ).execute()
        expect(stdio.stdout.getvalue()).to.eq('')

    def test_stdio_can_write_a_single_point(self):
        stdio.stdout = StringIO('')
        (
            emit(limit=1, start='2016-01-01')
            | write('stdio')
        ).execute()
        expect(json.loads(stdio.stdout.getvalue())).to.eq({
            'time': '2016-01-01T00:00:00.000Z'
        })

    def test_stdio_can_write_a_multiple_points(self):
        stdout = StringIO('')
        stdio.stdout = stdout
        (
            emit(limit=5, start='2016-01-01')
            | put(count=count())
            | write('stdio')
        ).execute()

        results = []
        stdio.stdin = StringIO(stdout.getvalue())
        (
            read('stdio')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'count': 1},
            {'time': '2016-01-01T00:00:01.000Z', 'count': 2},
            {'time': '2016-01-01T00:00:02.000Z', 'count': 3},
            {'time': '2016-01-01T00:00:03.000Z', 'count': 4},
            {'time': '2016-01-01T00:00:04.000Z', 'count': 5}
        ])

    def test_stdio_can_write_a_single_timeless_point(self):
        stdio.stdout = StringIO('')
        (
            emit(limit=1, start='2016-01-01')
            | put(foo='bar')
            | remove('time')
            | write('stdio')
        ).execute()
        expect(json.loads(stdio.stdout.getvalue())).to.eq({
            'foo': 'bar'
        })

    @mock.patch('flume.logger.warn')
    def test_stdio_can_write_a_multiple_timeless_points(self, mock_warn):
        stdout = StringIO('')
        stdio.stdout = stdout
        (
            emit(limit=5, start='2016-01-01')
            | put(count=count())
            | remove('time')
            | write('stdio')
        ).execute()

        results = []
        stdio.stdin = StringIO(stdout.getvalue())
        (
            read('stdio')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'count': 1},
            {'count': 2},
            {'count': 3},
            {'count': 4},
            {'count': 5}
        ])
        expect(mock_warn.call_args_list).to.eq([
            mock.call('point missing time field "time"'),
            mock.call('point missing time field "time"'),
            mock.call('point missing time field "time"'),
            mock.call('point missing time field "time"'),
            mock.call('point missing time field "time"')
        ])
