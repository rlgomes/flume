"""
intersect proc
"""
from collections import OrderedDict

from flume import node


class intersect(node):

    name = 'intersect'

    def __init__(self, *fieldnames):
        node.__init__(self)
        self.fieldnames = fieldnames

    def loop(self):
        inputs_count = self.input_count()

        if len(self.fieldnames) == 0:
            previous_point = None

            while self.running:
                points = self.pull()

                for point in points:
                    flume_path = point.__meta__.flume_path

                    if previous_point is None:
                        previous_point = point
                        previous_point.__meta__.inputs = set([flume_path])

                    elif previous_point.time == point.time:
                        previous_point.__meta__.inputs.add(flume_path)
                        previous_point.update(point)

                    else:
                        if len(previous_point.__meta__.inputs) == inputs_count:
                            self.push(previous_point)

                        previous_point = point
                        previous_point.__meta__.inputs = set([flume_path])

            if len(previous_point.__meta__.inputs) == inputs_count:
                self.push(previous_point)

        else:
            # when intersecting on non `time` field we basically buffer every
            # point and emit when we have a complete window

            # XXX: non time based result should have a limit on maximum
            #      amount of points to handle like 100K so we don't run out of
            #      memory

            result = OrderedDict()
            fieldnames = self.fieldnames
            while self.running:
                points = self.pull()

                for point in points:
                    flume_path = point.__meta__.flume_path
                    key = '.'.join([str(point[fname]) for fname in fieldnames])

                    if key not in result:
                        result[key] = point
                        result[key].__meta__.inputs = set([flume_path])

                    else:
                        result[key].__meta__.inputs.add(flume_path)
                        result[key].update(point)

            points = []

            for point in result.values():
                if len(point.__meta__.inputs) == inputs_count:
                    points.append(point)

            self.push(points)
