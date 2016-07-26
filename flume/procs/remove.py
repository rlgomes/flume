"""
remove processor
"""
from flume import node


class remove(node):
    """
    # remove

    The remove processor is used to to remove unwanted fields from the stream by
    specifying the ones you want to remove

    usage: ... | remove(field,...,fieldN) | ...

    """

    name = 'remove'

    def __init__(self, *fieldnames):
        node.__init__(self, *fieldnames)
        self.fieldnames = fieldnames

    def loop(self):
        while self.running:
            points = self.pull()

            for point in points:
                for fieldname in self.fieldnames:
                    if point.hasfield(fieldname):
                        del point[fieldname]

            self.push(points)
