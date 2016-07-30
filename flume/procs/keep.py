"""
keep processor
"""
from flume import node, Point


class keep(node):

    name = 'keep'

    def __init__(self, *fieldnames):
        node.__init__(self, *fieldnames)
        self.fieldnames = fieldnames

    def loop(self):
        while self.running:
            points = self.pull()
            points_out = []

            for point in points:
                new_point = Point()
                points_out.append(new_point)

                for fieldname in self.fieldnames:
                    if point.hasfield(fieldname):
                        new_point[fieldname] = point.lookup(fieldname)

            self.push(points_out)
