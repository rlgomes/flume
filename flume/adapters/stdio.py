"""
stdio adapter
"""
import sys

from flume.adapters.adapter import adapter
from flume.adapters import streamers
from flume.point import Point
from flume import logger, moment


class stdio(adapter):
    """
    stdio adapter

    Used to read/write points from standard IO which includes the stdin,
    stdout and stderr, but can also be used to read/write points to a
    file on the filesystem
    """

    name = 'stdio'

    stdout = sys.stdout
    stdin = sys.stdin

    def __init__(self,
                 time='time',
                 format='jsonl',
                 file=None,
                 **kwargs):
        self.time = time
        self.streamer = streamers.get_streamer(format, **kwargs)
        self.file = file

    def __read(self, stream):
        for point in self.streamer.read(stream):
            if self.time in point.keys():
                point['time'] = moment.date(point[self.time])

                if self.time != 'time':
                    del point[self.time]

                yield [Point(**point)]

            else:
                yield [Point(**point)]

    def read(self):
        if self.file is None:
            for point in self.__read(stdio.stdin):
                yield point

        else:
            with open(self.file, 'r') as stream:
                for point in self.__read(stream):
                    yield point

    def write(self, points):
        if self.file is None:
            self.streamer.write(stdio.stdout, points)

        else:
            with open(self.file, 'a') as stream:
                self.streamer.write(stream, points)

    def eof(self):
        self.streamer.eof(stdio.stdout)
