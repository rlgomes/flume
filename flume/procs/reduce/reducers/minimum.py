from flume import reducer


class minimum(reducer):

    def __init__(self, fieldname):
        self.fieldname = fieldname
        self.min = None

    def update(self, point):
        if self.min:
            if point[self.fieldname] < self.min:
                self.min = point[self.fieldname]
        else:
            self.min = point[self.fieldname]

    def result(self):
        return self.min

    def reset(self):
        self.min = None
