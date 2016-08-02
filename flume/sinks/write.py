"""
write sink
"""

from flume import adapters, sink


class write(sink):

    name = 'write'

    def __init__(self,
                 adapter,
                 batch=-1,
                 **kwargs):
        sink.__init__(self)
        cls = adapters.get_adapter(adapter, 'write')

        self.instance = cls(**kwargs)
        self.write = self.instance.write
        self.batch = batch

    def loop(self):
        buffered = []
        while self.running:
            points = self.pull()
            buffered += points

            if len(buffered) > 0:
                if self.batch == -1:
                    self.write(buffered)
                    buffered = []

                elif len(buffered) > self.batch:
                    self.write(buffered[:self.batch])
                    buffered = buffered[self.batch:]

        if len(buffered) > 0:
            self.write(buffered[:self.batch])

        self.instance.eof()
