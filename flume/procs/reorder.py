"""
reorder processor
"""
import bisect

from flume import logger, moment, node


class reorder(node):

    name = 'reorder'

    def __init__(self, delay=None):
        node.__init__(self)
        self.delay = delay

    def loop(self):
        points = []
        btimes = []
        buffered = []
        last = None

        while self.running:
            points = self.pull()

            for point in points:
                # each point is timestamped upon arrival and only emitted
                # after the `delay` specified
                point.__arrival_time__ = moment.now()

                if 'time' not in point.keys():
                    buffered.append(point)

                else:
                    index = bisect.bisect_left(btimes, point.time)
                    btimes.insert(index, point.time)
                    buffered.insert(index, point)

            result = []
            keep = []
            for point in buffered:
                if 'time' not in point:
                    del point.__arrival_time__
                    result.append(point)

                elif (point.__arrival_time__ + self.delay) <= moment.now():
                    if last is not None and last.time > point.time:
                        logger.warn('dropping point %s, arrived after %s' %
                                    (point, last))
                        continue
                
                    del point.__arrival_time__
                    result.append(point)
                    last = point

                else:
                    keep.append(point)

            buffered = keep
            btimes = [point.time for point in buffered]

            if result != []:
                self.push(result)

        result = []
        for point in buffered:
            del point.__arrival_time__
            result.append(point)

        if result != []:
            self.push(result)
