"""
memory sink
"""

from flume import sink
from flume.exceptions import FlumineException

class memory(sink):

    name = 'memory'

    def __init__(self, results):
        sink.__init__(self, results)

        if not isinstance(results, list):
            raise FlumineException('results must a list')

        self.results = results

    def loop(self):
        while self.running:
            points = self.pull()

            for point in points:
                self.results.append(point.json())
