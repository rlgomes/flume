"""
funcr reducer - transforms any existing function into a reducer that can be used
                in the flume pipeline
"""

from flume import reducer

def funcr(func):

    class wrapper_reducer(reducer):
        def __init__(self, *fieldnames):
            self.fieldnames = fieldnames
            self.value = None

        def update(self, point):
            self.value = func(*[point[fieldname] for fieldname in self.fieldnames])

        def result(self):
            return self.value

        def reset(self):
            self.value = None

    return wrapper_reducer
