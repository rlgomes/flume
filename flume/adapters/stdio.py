"""
stdio adapter
"""
import sys

from flume.adapters.adapter import adapter
from flume.adapters import streamers
from flume.point import Point


class InputStream(object):
    """
    Override the behaviour of readlines which doesn't actually stream data but
    attempts to read the whole input and break it into individual lines. We want
    the input to stream line by line and not block the pipeline.
    """

    def __init__(self, file):
        self.file = file

    def read(self, size=1024):
        return self.file.read(size=1024)

    def readlines(self):

        while True:
            line = self.file.readline()

            if not line:
                break

            yield line

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
                 format='jsonl',
                 file=None,
                 **kwargs):
        self.streamer = streamers.get_streamer(format, **kwargs)
        self.file = file

    def read(self):
        if self.file is None:
            for point in self.streamer.read(InputStream(stdio.stdin)):
                yield [Point(**point)]

        else:
            with open(self.file, 'r') as stream:
                stream = InputStream(stream)
                for point in self.streamer.read(stream):
                    yield [Point(**point)]

    def write(self, points):
        if self.file is None:
            self.streamer.write(stdio.stdout, points)

        else:
            with open(self.file, 'a') as stream:
                self.streamer.write(stream, points)

    def eof(self):
        self.streamer.eof(stdio.stdout)
