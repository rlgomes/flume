
import unittest

from flume import *
from flume.adapters.adapter import adapter

from robber import expect


class dummy(adapter):

    name = 'dummy'

    def __init__(self, result=[]):
        self.result = result

    def read(self):
        return self.result

    def write(self, points):
        for point in points:
            self.result.append(point.json())

register_adapter(dummy)

class WriteTest(unittest.TestCase):

    def test_write_can_handle_an_empty_stream(self):
        result = []
        (
            emit(points=[])
            | write('dummy', result=result)
        ).execute()
        expect(result).to.eq([])

    def test_write_can_handle_a_few_points(self):
        result = []
        (
            emit(points=[
                {'foo': 1},
                {'foo': 1},
                {'foo': 1}
            ])
            | write('dummy', result=result)
        ).execute()
        expect(result).to.eq([
            {'foo': 1},
            {'foo': 1},
            {'foo': 1}
        ])
