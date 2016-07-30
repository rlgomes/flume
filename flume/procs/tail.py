"""
tail processor
"""
from flume import node


class tail(node):

    name = 'tail'

    def __init__(self, howmany):
        node.__init__(self)
        self.howmany = howmany

    def loop(self):
        points = []

        while self.running:
            points += self.pull()
            points = points[-self.howmany:]

        self.push(points[-self.howmany:])
