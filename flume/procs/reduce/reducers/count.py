"""
count reducer
"""
from flume import reducer


class count(reducer):

    def __init__(self):
        self.count = 0

    def update(self, point):
        self.count += 1

    def result(self):
        return self.count

    def reset(self):
        self.count = 0
