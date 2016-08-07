"""
flume exceptions module
"""


class FlumineException(Exception):

    def __init__(self, message):
        # following may seem odd but necessary for this to work on both
        # python 2 and python 3
        Exception.__init__(self, message)
        self.message = message
