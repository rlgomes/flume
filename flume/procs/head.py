"""
head processor
"""
from flume import node


class head(node):

    name = 'head'

    def __init__(self, howmany):
        node.__init__(self)
        self.howmany = howmany

    def loop(self):
        points = []
        done = False

        while self.running:
            points += self.pull()

            if len(points) < self.howmany:
                continue

            if not done:
                done = True
                self.push(points[:self.howmany])

        if not done:
            done = True
            self.push(points[:self.howmany])
