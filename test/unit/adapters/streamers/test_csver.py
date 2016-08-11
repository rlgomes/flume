"""
csv streamer unittests
"""
import unittest

from robber import expect

from flume import Point
from flume.adapters.streamers import get_streamer
from test.unit.util import FakeIO


class CSVStreamerTest(unittest.TestCase):

    def test_csv_streamer_can_read_an_empty_stream(self):
        streamer = get_streamer('csv')
        stream = FakeIO('')
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([])

    def test_csv_streamer_can_read_a_single_point(self):
        streamer = get_streamer('csv')
        stream = FakeIO('time\n2016-01-01T00:00:00.000Z\n')

        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(time='2016-01-01T00:00:00.000Z')
        ])

    def test_csv_streamer_can_read_multiple_points(self):
        streamer = get_streamer('csv')
        stream = FakeIO('time,foo\n' +
                        '2016-01-01T00:00:00.000Z,1\n' +
                        '2016-01-01T00:00:01.000Z,2\n' +
                        '2016-01-01T00:00:02.000Z,3')
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(time='2016-01-01T00:00:00.000Z', foo='1'),
            Point(time='2016-01-01T00:00:01.000Z', foo='2'),
            Point(time='2016-01-01T00:00:02.000Z', foo='3')
        ])

    def test_csv_streamer_can_handle_blank_lines(self):
        streamer = get_streamer('csv')
        stream = FakeIO('time,foo\n' +
                        '2016-01-01T00:00:00.000Z,1\n' +
                        '\n' +
                        '2016-01-01T00:00:01.000Z,2\n')
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(time='2016-01-01T00:00:00.000Z', foo='1'),
            Point(time='2016-01-01T00:00:01.000Z', foo='2')
        ])

    def test_csv_streamer_can_write_an_empty_stream(self):
        streamer = get_streamer('csv')
        stream = FakeIO('')

        streamer.write(stream, [])
        stream = FakeIO(stream.getvalue())

        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([])

    def test_csv_streamer_can_write_a_single_point(self):
        streamer = get_streamer('csv')
        stream = FakeIO('')

        streamer.write(stream, [
            Point(time='2016-01-01T00:00:00.000Z')
        ])
        stream = FakeIO(stream.getvalue())

        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(time='2016-01-01T00:00:00.000Z')
        ])

    def test_csv_streamer_can_write_multiple_points(self):
        streamer = get_streamer('csv')
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
            Point(time='2016-01-01T00:00:00.000Z', foo='1'),
            Point(time='2016-01-01T00:00:01.000Z', foo='2'),
            Point(time='2016-01-01T00:00:02.000Z', foo='3')
        ])
