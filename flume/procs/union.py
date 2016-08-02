"""
union proc
"""
from collections import OrderedDict

from flume import node


class union(node):

    name = 'union'

    def __init__(self, *fieldnames):
        node.__init__(self)
        self.fieldnames = fieldnames

    def loop(self):
        points = []
        previous_point = None

        if len(self.fieldnames) == 0:
            while self.running:
                points = self.pull()

                for point in points:
                    if previous_point is None:
                        previous_point = point

                    elif previous_point.time == point.time:
                        previous_point.update(point)

                    else:
                        self.push(previous_point)
                        previous_point = point
            
            if previous_point is not None:
                self.push(previous_point)

        else:
            # when unioning on non `time` field we basically buffer every
            # point and emit when we have a complete window

            # XXX: non time based union should have a limit on maximum
            #      amount of points to handle like 100K so we don't run out of
            #      memory
            result = OrderedDict()
            fieldnames = self.fieldnames

            while self.running:
                points = self.pull()

                for point in points:
                    key = '.'.join([str(point[fname]) for fname in fieldnames])

                    if key not in result:
                        result[key] = point

                    else:
                        result[key].update(point)

            self.push([point for point in result.values()])
