"""
math reducers unittests
"""
import unittest

from robber import expect
from flume import *


class MathReducerTest(unittest.TestCase):

    def test_math_exp_log_reducers_work(self):
        results = []
        (
            emit(limit=3, every='0.001s')
            | put(count=count())
            | put(lvalue=math.log('count'))
            | put(value=math.exp('lvalue'))
            | keep('value')
            # handles rounding errors
            | put(value=math.floor('value'))
            | memory(results)
        ).execute()
        expect(results).to.eq([
            {'value': 1.0},
            {'value': 2.0},
            {'value': 3.0}
        ])

