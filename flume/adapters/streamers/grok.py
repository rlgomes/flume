"""
regex streamer
"""
import pygrok

from flume import Point
from flume.adapters.streamers.base import Streamer
from flume.exceptions import FlumineException


class Grok(Streamer):

    def __init__(self,
                 pattern='%{GREEDYDATA:message}'):
        self.pattern = pattern

    def read(self, stream):
        for line in stream.readlines():
            matches = pygrok.grok_match(line, self.pattern)
            yield Point(**matches)

    def write(self, stream, points):
        raise FlumineException('regex does not support writing data')
