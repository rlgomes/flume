"""
put proc unittests
"""
import unittest

from robber import expect
from flume import *


class PutTest(unittest.TestCase):

    def test_put_add_a_numerical_field(self):
        results = []
        (
            emit(points=[{}, {}])
            | put(foo=1)
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1},
            {'foo': 1}
        ])

    def test_put_multiple_fields(self):
        results = []
        (
            emit(points=[{}, {}])
            | put(foo=1, fizz='buzz')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1, 'fizz': 'buzz'},
            {'foo': 1, 'fizz': 'buzz'}
        ])

    def test_put_multiple_fields_with_multiple_puts(self):
        results = []
        (
            emit(points=[{}, {}])
            | put(foo=1)
            | put(fizz='buzz')
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'foo': 1, 'fizz': 'buzz'},
            {'foo': 1, 'fizz': 'buzz'}
        ])
