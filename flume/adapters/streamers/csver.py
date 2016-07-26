"""
csv streamer
"""
import csv

from flume.adapters.streamers.base import Streamer
from flume import Point


class CSV(Streamer):

    def __init__(self, headers=True):
        self.writer = None
        self.headers = headers

    def read(self, stream):
        # XXX: expose the delimiter, quotechar...etc.
        reader = csv.DictReader(stream)

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
