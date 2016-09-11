"""
emit benchmark tests
"""
import unittest

from robber import expect

from flume import *

import time

import six

class timer(object):

    def __init__(self, what, timeout=None):
        self.what = what
        self.timeout = timeout

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, exc_traceback):

        if exc_type is not None:
            six.reraise(exc_type, exc_value, exc_traceback)
        
        elapsed = time.time() - self.start
        if elapsed > self.timeout:
            raise Exception('%s took %ss which is longer than %ss' %
                            (self.what, elapsed, self.timeout))

class EmitTest(unittest.TestCase):

    def test_emit_100K_historical_points(self):
        with timer('emit', timeout=2):
            emit(limit=100000, start='1970-01-01').execute()

    def test_emit_100K_live_points(self):
        with timer('emit', timeout=3):
            emit(limit=100000, every='0.000001s').execute()
