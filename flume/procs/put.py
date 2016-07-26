"""
put processor
"""
from flume import node, reducer


class put(node):
    """
    # put

    The put processor is used to to add fields to any point that passes through
    this node in the pipeline. The fields added can be static or the result of
    applying a **reducer**.

    usage: ... | put(field=value, ..., field=count()) | ...

    """

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
                        point[key] = value

            self.push(points)
