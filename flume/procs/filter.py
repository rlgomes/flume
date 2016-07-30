"""
filter processor
"""
import ast
import inspect

from flume import node

def islambda(something):
    return inspect.isfunction(something) and something.__name__ == '<lambda>'

class filter(node):

    name = 'filter'

    def __init__(self, filter_expression):
        node.__init__(self, filter_expression)
        self.filter = filter.parse_filter_expression(filter_expression)

    @classmethod
    def parse_filter_expression(cls, filter_expression):
        if isinstance(filter_expression, str):
            def wrap_eval(point):
                """
                wraps a filter expression encoded as a string 'a < "b"'
                """
                return eval(filter_expression, {}, point)

            return wrap_eval

        else:
            raise Exception('unsupported filter type "%s"' % type(filter_expression))

    def loop(self):

        while self.running:
            points = self.pull()
            points_out = []

            for point in points:
                if self.filter(point):
                    points_out.append(point)

            self.push(points_out)
