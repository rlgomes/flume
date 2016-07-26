"""
json streamer
"""
import ijson
import json

from flume.adapters.streamers.base import Streamer
from flume.point import Point

class JSON(Streamer):

    def __init__(self, pretty=False):
        self.pretty = pretty
        self.first_point = True
        self.start = False
        self.writing = False

    def read(self, stream):
        for point in ijson.items(stream, 'item'):
            yield Point(**point)

    def write(self, stream, points):
        self.writing = True

        if not self.start:
            stream.write('[\n')
            self.start = True

        for point in points:
            if not self.first_point:
                stream.write(',\n')

            else:
                self.first_point = False

            if self.pretty:
                # you can sort the keys in pretty jsonl format but indenting
                # would mean breaking the jsonl format
                string = json.dumps(point.json(), sort_keys=True, indent=4)

            else:
                string = json.dumps(point.json())

            stream.write('%s' % string)

    def eof(self, stream):
        if self.writing:
            stream.write('\n]')
