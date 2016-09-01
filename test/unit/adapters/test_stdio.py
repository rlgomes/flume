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
from test.unit.util import redirect


class StdioTest(unittest.TestCase):

    def test_can_read_from_empty(self):
        results = []

        with redirect(input=''):
            (
                read('stdio')
                | memory(results)
            ).execute()

        expect(results).to.eq([])

    def test_can_read_and_strip_ansi_sequences_from_terminal(self):
        results = []

        with redirect(input='''\033[1;32m pid cmd cpu\033[0m
1 init 0.0
2 bash 2.0
25 blah 3.0'''):
            (
                read('stdio', format='csv', delimiter=' ', strip_ansi=True)
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {'pid': '1', 'cmd': 'init', 'cpu': '0.0'},
            {'pid': '2', 'cmd': 'bash', 'cpu': '2.0'},
            {'pid': '25', 'cmd': 'blah', 'cpu': '3.0'}
        ])

    def test_can_read_and_strip_ansi_sequences_from_jsonl(self):
        results = []

        with redirect(input='{"time": "2016-01-01T00:00:00.000Z", "foo": "\033[1;32mbar\033[0m"}'):
            (
                read('stdio', format='jsonl', strip_ansi=True)
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}
        ])

    def test_can_read_and_strip_ansi_sequences_from_json(self):
        results = []

        with redirect(input='[{"time": "2016-01-01T00:00:00.000Z", "foo": "\033[1;32mbar\033[0m"}]'):
            (
                read('stdio', format='json', strip_ansi=True)
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}
        ])

    def test_can_read_and_not_strip_ansi_sequences_from_json(self):
        results = []

        with redirect(input='[{"time": "2016-01-01T00:00:00.000Z", "foo": "\033[1;32mbar\033[0m"}]'):
            (
                read('stdio', format='json')
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "\033[1;32mbar\033[0m"}
        ])

    def test_can_read_a_single_point(self):
        results = []

        with redirect(input='{"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}'):
            (
                read('stdio', format='jsonl')
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": "bar"}
        ])

    def test_can_read_multiple_points(self):
        results = []

        with redirect(input='{"time": "2016-01-01T00:00:00.000Z", "foo": 1}\n' +
                            '{"time": "2016-01-01T00:01:00.000Z", "foo": 2}\n' +
                            '{"time": "2016-01-01T00:02:00.000Z", "foo": 3}\n'):
            (
                read('stdio', format='jsonl')
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": 1},
            {"time": "2016-01-01T00:01:00.000Z", "foo": 2},
            {"time": "2016-01-01T00:02:00.000Z", "foo": 3}
        ])

    def test_can_read_a_single_timeless_point(self):
        results = []

        with redirect(input='{"foo": "bar"}'):
            (
                read('stdio', format='jsonl')
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {"foo": "bar"}
        ])

    def test_can_read_multiple_timeless_points(self):
        results = []

        with redirect(input='{"foo": 1}\n{"foo": 2}\n{"foo": 3}\n'):
            (
                read('stdio', format='jsonl')
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {"foo": 1},
            {"foo": 2},
            {"foo": 3}
        ])

    def test_can_read_multiple_points_with_custom_timefield(self):
        results = []

        with redirect(input='{"bar": "2016-01-01T00:00:00.000Z", "foo": 1}\n' +
                            '{"bar": "2016-01-01T00:01:00.000Z", "foo": 2}\n' +
                            '{"bar": "2016-01-01T00:02:00.000Z", "foo": 3}\n'):
            (
                read('stdio', format='jsonl', time='bar')
                | memory(results)
            ).execute()

        expect(results).to.eq([
            {"time": "2016-01-01T00:00:00.000Z", "foo": 1},
            {"time": "2016-01-01T00:01:00.000Z", "foo": 2},
            {"time": "2016-01-01T00:02:00.000Z", "foo": 3}
        ])

    def test_can_write_nothing(self):
        with redirect(input='') as io:
            (
                read('stdio')
                | write('stdio')
            ).execute()
        expect(io.stdout).to.eq('')

    def test_can_write_a_single_point(self):
        with redirect(input='') as io:
            (
                emit(limit=1, start='2016-01-01')
                | write('stdio')
            ).execute()

        expect(json.loads(io.stdout)).to.eq({
            'time': '2016-01-01T00:00:00.000Z'
        })

    def test_can_write_a_multiple_points(self):
        with redirect() as io:
            (
                emit(limit=5, start='2016-01-01')
                | put(count=count())
                | write('stdio')
            ).execute()

        results = []
        with redirect(input=io.stdout):
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

    def test_can_write_a_single_timeless_point(self):
        with redirect(input='') as io:
            (
                emit(limit=1, start='2016-01-01')
                | put(foo='bar')
                | remove('time')
                | write('stdio')
            ).execute()
        expect(json.loads(io.stdout)).to.eq({
            'foo': 'bar'
        })

    def test_can_write_a_multiple_timeless_points(self):
        with redirect(input='') as io:
            (
                emit(limit=5, start='2016-01-01')
                | put(count=count())
                | remove('time')
                | write('stdio')
            ).execute()

        results = []

        with redirect(input=io.stdout):
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

    def test_can_read_a_single_point_from_a_file(self):
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

    def test_can_write_a_single_point_to_a_file(self):
        _, tmpfile = tempfile.mkstemp()

        (
            emit(limit=1, start='2016-01-01')
            | write('stdio', file=tmpfile)
        ).execute()

        with open(tmpfile, 'r') as tmp_input:
            expect(json.loads(tmp_input.read())).to.eq({
                'time': '2016-01-01T00:00:00.000Z'
            })


    def test_can_write_override_single_point_to_a_file(self):
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

    def test_can_write_append_multiple_points_to_a_file(self):
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

    def test_raises_exception_on_invalid_compression_on_write(self):
        with self.assertRaisesRegexp(FlumeException, 'unsupported compression \[bananas\]'):
            (
                emit(limit=1, start='2016-01-01')
                | write('stdio', format='jsonl', compression='bananas')
            ).execute()

    def test_raises_exception_on_invalid_compression_on_read(self):
        with self.assertRaisesRegexp(FlumeException, 'unsupported compression \[bananas\]'):
            (
                read('stdio', format='jsonl', compression='bananas')
            ).execute()

    def test_can_write_and_read_a_single_point_in_jsonl_with_zlib_compression(self):
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

    def test_can_write_and_read_a_single_point_in_jsonl_with_gzip_compression(self):
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

    def test_can_write_and_read_a_single_point_in_csv_with_deflate_compression(self):
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

    def test_optimizes_head(self):
        results = []

        a = read('stdio',
                 format='grok',
                 file='test/unit/adapters/inputs/long.log')
        b = head(5)
        c = memory(results)
        (a | b | c).execute()

        expect(results).to.have.length(5)
        expect(a.stats.points_pushed).to.eq(5)
        expect(a.stats.points_pulled).to.eq(0)

        expect(b.stats.points_pushed).to.eq(0)
        expect(b.stats.points_pulled).to.eq(0)

        expect(c.stats.points_pushed).to.eq(0)
        expect(c.stats.points_pulled).to.eq(5)
