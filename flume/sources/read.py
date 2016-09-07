"""
read source
"""
from flume import adapters, node


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
                 **kwargs):
        node.__init__(self)
        cls = adapters.get_adapter(adapter, 'read')

        self.instance = cls(**kwargs)
        self.read = self.instance.read

    def loop(self):
        if self.child is not None and self.config.optimize:
            self.instance.optimize(self.child)

        for points in self.read():
            self.push(points)
