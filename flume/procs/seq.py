"""
seq proc
"""
from flume import node, queue

class pipe(node):

    def loop(self):
        while self.running:
            points = self.pull()
            self.push(points)

    def push(self, points):
        node.push(self, [point for point in points if point != self.EOF])

class seq(node):

    name = 'seq'

    def __init__(self, *pipelines):
        node.__init__(self)
        self.pipelines = pipelines

    def loop(self):
        for pipeline in self.pipelines:
            outputs = list(self.outputs)

            node.init_node(pipeline,
                           inputs=None,
                           outputs=[queue()],
                           parent=None,
                           source=None)

            connector = pipe()
            node.init_node(connector,
                           inputs=pipeline.outputs,
                           outputs=outputs,
                           parent=pipeline,
                           source=None)

            connector.execute(wait=True)
