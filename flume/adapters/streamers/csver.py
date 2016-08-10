"""
csv streamer
"""
import csv

from flume.adapters.streamers.base import Streamer
from flume import Point


class CSV(Streamer):

    def __init__(self,
                 headers=True,
                 delimiter=',',
                 ignore_whitespace=True):
        self.writer = None
        self.headers = headers
        self.delimiter = delimiter
        self.ignore_whitespace = ignore_whitespace

    def read(self, stream):
        reader = csv.DictReader(stream.readlines(),
                                delimiter=self.delimiter,
                                skipinitialspace=self.ignore_whitespace)

        for point in reader:
            # XXX: buffer N points before pushing out ? 
            yield Point(**point)

    def write(self, stream, points):
        for point in points:
            point = point.json()

            if self.writer is None:
                fieldnames = point.keys()
                self.writer = csv.DictWriter(stream, fieldnames=fieldnames)
                if self.headers:
                    self.writer.writeheader()

            self.writer.writerow(point)
