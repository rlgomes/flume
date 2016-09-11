"""
union proc
"""
from collections import OrderedDict

from flume import node, Point


class union(node):

    name = 'union'

    def __init__(self, *fieldnames):
        node.__init__(self)
        self.fieldnames = fieldnames

    def loop(self):
        points = []
        union_points = []

        def unionize(points):
            """
            unionizes these points in order they appear in the list which 
            means the last point in the last overrides any previous field values
            """
            upoint = Point()

            for point in points:
                upoint.update(point)

            return upoint

        if len(self.fieldnames) == 0:
            while self.running:
                points = self.pull()

                for point in points:
                    if union_points == []:
                        union_points.insert(point.__meta__.input_index, point)

                    elif union_points[0].time == point.time:
                        union_points.insert(point.__meta__.input_index, point)

                    else:
                        point_to_push = unionize(union_points)
                        self.push(point_to_push)
                        union_points = [point]

            if union_points != []:
                point_to_push = unionize(union_points)
                self.push(point_to_push)

        else:
            # when unioning on non-time field we basically buffer every
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
