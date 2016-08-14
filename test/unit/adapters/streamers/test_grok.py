"""
grok streamer unittests
"""
import unittest

from test.unit.util import FakeIO

from robber import expect

from flume import Point
from flume.adapters.streamers import get_streamer


class GrokStreamerTest(unittest.TestCase):

    def test_grok_streamer_can_read_an_empty_stream(self):
        streamer = get_streamer('grok')
        stream = FakeIO('')
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([])

    def test_grok_streamer_can_read_a_single_point_with_default_pattern(self):
        streamer = get_streamer('grok')
        stream = FakeIO('just a simple line')

        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(message='just a simple line')
        ])

    def test_grok_streamer_can_read_multiple_points_with_default_pattern(self):
        streamer = get_streamer('grok')
        stream = FakeIO('one log line\n' +
                        'another log line\n' +
                        'yet another log line\n')

        points = []
        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(message='one log line'),
            Point(message='another log line'),
            Point(message='yet another log line')
        ])

    def test_grok_streamer_can_handle_blank_lines_with_default_pattern(self):
        streamer = get_streamer('grok')
        stream = FakeIO('one log line\n' +
                        '\n' +
                        'another log line\n' +
                        '\n' +
                        'yet another log line\n')
        points = []

        for point in streamer.read(stream):
            points.append(point)

        expect(points).to.eq([
            Point(message='one log line'),
            Point(message=''),
            Point(message='another log line'),
            Point(message=''),
            Point(message='yet another log line')
        ])

