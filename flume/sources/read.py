"""
read source
"""

from flume import adapters, logger, moment, node


class read(node):
    """
    read

    usage:
        read('adapter', [adapter arguments]) | ...  
    The read source can be used to read points from various adapters of which
    include the following:
    """

    name = 'read'

    def __init__(self,
                 adapter,
                 time='time',
                 **kwargs):
        node.__init__(self)
        cls = adapters.get_adapter(adapter, 'read')

        self.instance = cls(**kwargs)
        self.read = self.instance.read
        self.time = time

    def loop(self):
        for points in self.read():

            for point in points:
                if self.time in point:
                    point.time = moment.date(point[self.time])
                    if self.time != 'time':
                        del point[self.time]

            self.push(points)
