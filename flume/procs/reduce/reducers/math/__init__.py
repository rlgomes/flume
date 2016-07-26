"""
math reducer - exposes the python mathematical functions as flume reducers
"""
import inspect

import math as realmath
from flume import reducer


# XXX: we could export this to be used to wrap any python function
def ReducerWrapper(func):

    class python_math_reducer(reducer):
        """
        a reducer that handles wrapping the provided function as a reducer
        over a single field
        """

        def __init__(self, fieldname):
            self.fieldname = fieldname
            self.value = None

        def update(self, point):
            self.value = func(point[self.fieldname])

        def result(self):
            return self.value

        def reset(self):
            self.value = None

    return python_math_reducer


class math(object):

    ceil = ReducerWrapper(realmath.ceil)
    fabs = ReducerWrapper(realmath.fabs)
    floor = ReducerWrapper(realmath.floor)
    factorial = ReducerWrapper(realmath.factorial)
    fmod = ReducerWrapper(realmath.fmod)
    trunc = ReducerWrapper(realmath.trunc)
    isinf = ReducerWrapper(realmath.isinf)
    isnan = ReducerWrapper(realmath.isnan)

    exp = ReducerWrapper(realmath.exp)
    expm1 = ReducerWrapper(realmath.expm1)
    log = ReducerWrapper(realmath.log)
    log1p = ReducerWrapper(realmath.log1p)
    log10 = ReducerWrapper(realmath.log10)
    pow = ReducerWrapper(realmath.pow)
    sqrt = ReducerWrapper(realmath.sqrt)

    acos = ReducerWrapper(realmath.acos)
    asin = ReducerWrapper(realmath.asin)
    atan = ReducerWrapper(realmath.atan)
    atan2 = ReducerWrapper(realmath.atan2)

    cos = ReducerWrapper(realmath.cos)
    sin = ReducerWrapper(realmath.sin)
    tan = ReducerWrapper(realmath.tan)

    degrees = ReducerWrapper(realmath.degrees)
    radians = ReducerWrapper(realmath.radians)
