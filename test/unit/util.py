"""
testing utilities
"""

import sys

__IS_PY2 = sys.version[0] == '2'

class FakeIO(object):

    def __init__(self, data=''):
        self.data = data

    def close(self):
        pass

    def flush(self):
        pass

    def read(self, size):
        result = self.data[:size]
        self.data = self.data[size:]
        return result

    def readline(self, limit=-1):
        index = self.data.find('\n')

        if index == -1 and len(self.data) != 0:
            result = self.data
            self.data = ''
            return result

        result = self.data[:index + 1]
        self.data = self.data[index + 1:]
        return result

    def readlines(self):
        while True:
            line = self.readline()

            if not line:
                break

            yield line

    def write(self, data):
        self.data += data

    def getvalue(self):
        return self.data
