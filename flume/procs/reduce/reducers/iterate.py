"""
iterate reducer
"""
from flume import reducer


class iterate(reducer):

    def __init__(self, values):
        self.values = values
        self.index = -1

    def update(self, point):
        self.index += 1

    def result(self):
        return self.values[self.index % len(self.values)]

    def reset(self):
        self.index = 0
