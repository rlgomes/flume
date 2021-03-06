"""
jsonl streamer unittests
"""
import unittest

from robber import expect

from flume.adapters.streamers import get_streamer
from flume import Point
from test.unit.util import FakeIO


class JSONLStreamerTest(unittest.TestCase):

    def test_jsonl_streamer_can_read_an_empty_stream(self):
        streamer = get_streamer('jsonl')
        stream = FakeIO('')
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([])

    def test_jsonl_streamer_can_read_a_single_point(self):
        streamer = get_streamer('jsonl')
        stream = FakeIO('{"foo": "bar"}')
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([Point(foo='bar')])

    def test_jsonl_streamer_can_read_multiple_points(self):
        streamer = get_streamer('jsonl')
        stream = FakeIO("""{"time": "2016-01-01T00:00:00.000Z", "foo": 1}
        {"time": "2016-01-01T00:00:01.000Z", "foo": 2}
        {"time": "2016-01-01T00:00:02.000Z", "foo": 3}""")
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(time='2016-01-01T00:00:00.000Z', foo=1),
            Point(time='2016-01-01T00:00:01.000Z', foo=2),
            Point(time='2016-01-01T00:00:02.000Z', foo=3),
        ])

    def test_jsonl_streamer_can_handle_blank_lines(self):
        streamer = get_streamer('jsonl')
        stream = FakeIO("""
        {"time": "2016-01-01T00:00:00.000Z", "foo": 1}
        {"time": "2016-01-01T00:00:01.000Z", "foo": 2}
        """)
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(time='2016-01-01T00:00:00.000Z', foo=1),
            Point(time='2016-01-01T00:00:01.000Z', foo=2)
        ])

    def test_jsonl_streamer_can_write_an_empty_stream(self):
        streamer = get_streamer('jsonl')
        stream = FakeIO('')

        streamer.write(stream, [])
        stream = FakeIO(stream.getvalue())

        points = []
        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([])

    def test_jsonl_streamer_write_a_single_point(self):
        streamer = get_streamer('jsonl')
        stream = FakeIO('')

        streamer.write(stream, [Point(foo='bar')])
        stream = FakeIO(stream.getvalue())

        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([Point(foo='bar')])

    def test_jsonl_streamer_write_a_single_pretty_point(self):
        streamer = get_streamer('jsonl', pretty=True)
        stream = FakeIO('')

        streamer.write(stream, [Point(foo='bar')])
        stream = FakeIO(stream.getvalue())

        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([Point(foo='bar')])

    def test_jsonl_streamer_can_write_multiple_points(self):
        streamer = get_streamer('jsonl')
        stream = FakeIO('')

        streamer.write(stream, [
            Point(time='2016-01-01T00:00:00.000Z', foo=1),
            Point(time='2016-01-01T00:00:01.000Z', foo=2),
            Point(time='2016-01-01T00:00:02.000Z', foo=3)
        ])
        stream = FakeIO(stream.getvalue())

        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(time='2016-01-01T00:00:00.000Z', foo=1),
            Point(time='2016-01-01T00:00:01.000Z', foo=2),
            Point(time='2016-01-01T00:00:02.000Z', foo=3)
        ])
