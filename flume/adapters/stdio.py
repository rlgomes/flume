"""
stdio adapter
"""
import re
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

    def __init__(self, stream, strip_ansi=False):
        self.stream = stream 
        self.strip_ansi = strip_ansi

    def __remove_ansi(self, line):
        if line is None:
            return None

        return re.sub(r'\x1b[^A-Za-z]*[A-Za-z]', '', line)

    def read(self, size=1024):
        if self.strip_ansi:
            return self.__remove_ansi(self.stream.read(size))

        else:
            return self.stream.read(size)

    def readlines(self):

        while True:
            line = self.stream.readline()

            if not line:
                break

            if self.strip_ansi:
                yield self.__remove_ansi(line)

            else:
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
                 append=False,
                 strip_ansi=False,
                 **kwargs):
        self.streamer = streamers.get_streamer(format, **kwargs)
        self.file = file
        self.append = append
        self.strip_ansi = strip_ansi

    def read(self):
        if self.file is None:
            for point in self.streamer.read(InputStream(stdio.stdin,
                                                        strip_ansi=self.strip_ansi)):
                yield [Point(**point)]

        else:
            with open(self.file, 'r') as stream:
                stream = InputStream(stream,
                                     strip_ansi=self.strip_ansi)
                for point in self.streamer.read(stream):
                    yield [Point(**point)]

    def write(self, points):
        if self.file is None:
            self.streamer.write(stdio.stdout, points)

        else:
            if self.append:
                mode = 'a'

            else:
                mode = 'w'

            with open(self.file, mode) as stream:
                self.streamer.write(stream, points)

    def eof(self):
        self.streamer.eof(stdio.stdout)
