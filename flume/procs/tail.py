"""
tail processor
"""
from flume import node


class tail(node):
    """
    # tail

    The tail processor is used to only keep the last N elements and throw
    away all other remaining points

    usage: ... | tail(N) | ...

    """

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
