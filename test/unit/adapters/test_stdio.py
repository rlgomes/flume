# coding utf-8
"""
http adapter unittests
"""

import json
import sys
import tempfile
import unittest
import zlib

import mock

from robber import expect

from flume import *
from test.unit.util import FakeIO


class StdioTest(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        # make sure to set the stdin/stdout hooks in stdio back to the
        # right values
        stdio.stdin = sys.stdin
        stdio.stdout = sys.stdout

    def test_stdio_can_read_from_empty(self):
        stdio.stdin = FakeIO('')
        results = []

        (
            read('stdio')
            | memory(results)
        ).execute()
        expect(results).to.eq([])

    def test_stdio_can_read_and_strip_ansi_sequences_from_terminal(self):
        stdio.stdin = FakeIO('''\033[1;32m pid cmd cpu\033[0m
1 init 0.0
2 bash 2.0
25 blah 3.0''')
        results = []

        (
            read('stdio', format='csv', delimiter=' ', strip_ansi=True)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'pid': '1', 'cmd': 'init', 'cpu': '0.0'},
            {'pid': '2', 'cmd': 'bash', 'cpu': '2.0'},
            {'pid': '25', 'cmd': 'blah', 'cpu': '3.0'}
        ])

    def test_stdio_can_read_and_strip_ansi_sequences_from_jsonl(self):
        stdio.stdin = FakeIO('{"time": "2016-01-01T00:00:00.000Z", "foo": "\033[1;32mbar\033[0m"}')
        results = []

        (
            read('stdio', format='jsonl', strip_ansi=True)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}
        ])

    def test_stdio_can_read_and_strip_ansi_sequences_from_json(self):
        stdio.stdin = FakeIO('[{"time": "2016-01-01T00:00:00.000Z", "foo": "\033[1;32mbar\033[0m"}]')
        results = []

        (
            read('stdio', format='json', strip_ansi=True)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}
        ])

    def test_stdio_can_read_and_not_strip_ansi_sequences_from_json(self):
        stdio.stdin = FakeIO('[{"time": "2016-01-01T00:00:00.000Z", "foo": "\033[1;32mbar\033[0m"}]')
        results = []

        (
            read('stdio', format='json')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "\033[1;32mbar\033[0m"}
        ])

    def test_stdio_can_read_a_single_point(self):
        stdio.stdin = FakeIO('{"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}')
        results = []

        (
            read('stdio', format='jsonl')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}
        ])

    def test_stdio_can_read_multiple_points(self):
        stdio.stdin = FakeIO('{"time": "2016-01-01T00:00:00.000Z", "foo": 1}\n' +
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

    def test_stdio_can_read_a_single_timeless_point(self):
        stdio.stdin = FakeIO('{"foo": "bar"}')
        results = []

        (
            read('stdio', format='jsonl')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"foo": "bar"}
        ])

    def test_stdio_can_read_multiple_timeless_points(self):
        stdio.stdin = FakeIO('{"foo": 1}\n{"foo": 2}\n{"foo": 3}\n')
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

    def test_stdio_can_read_multiple_points_with_custom_timefield(self):
        stdio.stdin = FakeIO('{"bar": "2016-01-01T00:00:00.000Z", "foo": 1}\n' +
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
        stdio.stdin = FakeIO('')
        stdio.stdout = FakeIO('')
        (
            read('stdio')
            | write('stdio')
        ).execute()
        expect(stdio.stdout.getvalue()).to.eq('')

    def test_stdio_can_write_a_single_point(self):
        stdio.stdout = FakeIO('')
        (
            emit(limit=1, start='2016-01-01')
            | write('stdio')
        ).execute()
        expect(json.loads(stdio.stdout.getvalue())).to.eq({
            'time': '2016-01-01T00:00:00.000Z'
        })

    def test_stdio_can_write_a_multiple_points(self):
        stdout = FakeIO('')
        stdio.stdout = stdout
        (
            emit(limit=5, start='2016-01-01')
            | put(count=count())
            | write('stdio')
        ).execute()

        results = []
        stdio.stdin = FakeIO(stdout.getvalue())
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
        stdio.stdout = FakeIO('')
        (
            emit(limit=1, start='2016-01-01')
            | put(foo='bar')
            | remove('time')
            | write('stdio')
        ).execute()
        expect(json.loads(stdio.stdout.getvalue())).to.eq({
            'foo': 'bar'
        })

    def test_stdio_can_write_a_multiple_timeless_points(self):
        stdout = FakeIO('')
        stdio.stdout = stdout
        (
            emit(limit=5, start='2016-01-01')
            | put(count=count())
            | remove('time')
            | write('stdio')
        ).execute()

        results = []
        stdio.stdin = FakeIO(stdout.getvalue())
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

    def test_stdio_can_read_a_single_point_from_a_file(self):
        _, tmpfile = tempfile.mkstemp()

        with open(tmpfile, 'w') as output:
            output.write('{"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}')

        results = []
        (
            read('stdio', file=tmpfile)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}
        ])

    def test_stdio_can_write_a_single_point_to_a_file(self):
        _, tmpfile = tempfile.mkstemp()

        (
            emit(limit=1, start='2016-01-01')
            | write('stdio', file=tmpfile)
        ).execute()

        with open(tmpfile, 'r') as tmp_input:
            expect(json.loads(tmp_input.read())).to.eq({
                'time': '2016-01-01T00:00:00.000Z'
            })


    def test_stdio_can_write_override_single_point_to_a_file(self):
        _, tmpfile = tempfile.mkstemp()

        (
            emit(limit=1, start='2015-01-01')
            | write('stdio', file=tmpfile)
        ).execute()

        (
            emit(limit=1, start='2016-01-01')
            | write('stdio', file=tmpfile, append=False)
        ).execute()

        with open(tmpfile, 'r') as tmp_input:
            expect(json.loads(tmp_input.read())).to.eq({
                'time': '2016-01-01T00:00:00.000Z'
            })

    def test_stdio_can_write_append_multiple_points_to_a_file(self):
        _, tmpfile = tempfile.mkstemp()

        (
            emit(limit=1, start='2015-01-01')
            | write('stdio', file=tmpfile)
        ).execute()

        (
            emit(limit=1, start='2016-01-01')
            | write('stdio', file=tmpfile, append=True)
        ).execute()
        
        results = []

        (
            read('stdio', file=tmpfile)
            | memory(results)
        ).execute() 
        expect(results).to.eq([
            {'time': '2015-01-01T00:00:00.000Z'},
            {'time': '2016-01-01T00:00:00.000Z'}
        ])

    def test_stdio_raises_exception_on_invalid_compression_on_write(self):
        with self.assertRaisesRegexp(FlumineException, 'unsupported compression \[bananas\]'):
            (
                emit(limit=1, start='2016-01-01')
                | write('stdio', format='jsonl', compression='bananas')
            ).execute()

    def test_stdio_raises_exception_on_invalid_compression_on_read(self):
        with self.assertRaisesRegexp(FlumineException, 'unsupported compression \[bananas\]'):
            (
                read('stdio', format='jsonl', compression='bananas')
            ).execute()

    def test_stdio_can_write_and_read_a_single_point_in_jsonl_with_zlib_compression(self):
        _, tmpfile = tempfile.mkstemp()
        (
            emit(limit=1, start='2016-01-01')
            | write('stdio', file=tmpfile, format='jsonl', compression='zlib')
        ).execute()

        results = []
        (
            read('stdio', file=tmpfile, format='jsonl', compression='zlib')
            | memory(results)
        ).execute()
        expect(results).to.eq([{"time": "2016-01-01T00:00:00.000Z"}])

    def test_stdio_can_write_and_read_a_single_point_in_jsonl_with_gzip_compression(self):
        _, tmpfile = tempfile.mkstemp()
        (
            emit(limit=1, start='2016-01-01')
            | write('stdio', file=tmpfile, format='jsonl', compression='gzip')
        ).execute()

        results = []
        (
            read('stdio', file=tmpfile, format='jsonl', compression='gzip')
            | memory(results)
        ).execute()
        expect(results).to.eq([{"time": "2016-01-01T00:00:00.000Z"}])

    def test_stdio_can_write_and_read_a_single_point_in_csv_with_deflate_compression(self):
        _, tmpfile = tempfile.mkstemp()
        (
            emit(limit=1, start='2016-01-01')
            | write('stdio', file=tmpfile, format='csv', compression='deflate')
        ).execute()

        results = []
        (
            read('stdio', file=tmpfile, format='csv', compression='deflate')
            | memory(results)
        ).execute()
        expect(results).to.eq([{"time": "2016-01-01T00:00:00.000Z"}])
