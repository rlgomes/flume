"""
put processor
"""
from flume import node, reducer
from flume.util import is_string

class put(node):

    name = 'put'

    def __init__(self, **fields):
        node.__init__(self, **fields)
        self.fields = fields

    def loop(self):
        while self.running:
            points = self.pull()

            for point in points:
                # call update every time through here
                for (key, value) in self.fields.items():
                    if isinstance(value, reducer):
                        value.update(point)
                        point[key] = value.result()

                    else:
                        if is_string(value):
                            point[key] = value.format(**point.json())

                        else:
                            point[key] = value

            self.push(points)
