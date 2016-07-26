from flume import reducer

class maximum(reducer):

    def __init__(self, fieldname):
        self.fieldname = fieldname
        self.max = None

    def update(self, point):
        if self.max:
            if point[self.fieldname] > self.max:
                self.max = point[self.fieldname]
        else:
            self.max = point[self.fieldname]

    def result(self):
        return self.max

    def reset(self):
        self.max = None
