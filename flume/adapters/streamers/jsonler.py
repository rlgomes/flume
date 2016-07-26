"""
jsonl streamer
"""
import json

from flume.adapters.streamers.base import Streamer
from flume import Point


class JSONL(Streamer):

    def __init__(self, pretty=False):
        self.pretty = pretty

    def read(self, stream):
        for line in stream.readlines():

            # skip blank lines
            if len(line.strip()) == 0:
                continue

            point = json.loads(line)
            yield Point(**point)

    def write(self, stream, points):
        for point in points:
            if self.pretty:
                # you can sort the keys in pretty jsonl format but indenting
                # would mean breaking the jsonl format
                string = json.dumps(point.json(), sort_keys=True)

            else:
                string = json.dumps(point.json())

            stream.write('%s\n' % string)
