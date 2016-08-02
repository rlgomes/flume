"""
sort processor
"""
import operator

from flume import node
from flume.exceptions import FlumineException


class sort(node):

    name = 'sort'

    def __init__(self, *fieldnames, **kwargs):
        node.__init__(self, *fieldnames)
        self.fieldnames = fieldnames

        if 'limit' in kwargs:
            self.limit = kwargs['limit']

        else:
            self.limit = 100000

        if 'order' in kwargs:
            order = kwargs['order']

            if order not in ['asc', 'desc']:
                raise FlumineException('order can be "asc" or "desc", not "%s"' % order)

            self.order = order

        else:
            self.order = 'asc'

    def loop(self):
        result = []

        while self.running:
            points = self.pull()

            if len(result) > self.limit:
                raise FlumineException('sort buffer overflown, limit is %s, buffering %s' %
                                       (self.limit, len(result)))

            result += points

        if len(self.fieldnames) > 0:
            result = sorted(result,
                            key=operator.attrgetter(*self.fieldnames),
                            reverse=(self.order == 'desc'))

            # XXX: we could remove the field while we sort to make this a bit
            #      more efficient
            for point in result:
                if 'time' in point:
                    del point['time']

        self.push(result)
