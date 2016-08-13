"""
common module

- defines various basic elements of what make up a flume pipeline
- handles all of the fancy logic for the dot(.) and pipe(|) notation when
  construction pipelines
"""
import bisect
import logging
import sys
import threading

import six

from flume import moment
from flume import logger
from flume import util

if util.IS_PY2:
    from Queue import Empty
    from Queue import Queue as queue

else:
    from queue import Queue as queue
    from queue import Empty

from flume.exceptions import FlumineException
from flume.point import Point


__SOURCES = {}
__PROCS = {}
__SINKS = {}


def build_node_func(which_node):
    """
    internally used method to attach new nodes to existing ones in the flume
    pipeline when registering such elements
    """

    def node_func(self, *args, **kwargs):
        """
        internal method responsible for hooking up the nodes in a flume
        pipeline
        """

        node_instance = which_node(*args, **kwargs)

        if not hasattr(self, 'outputs'):
            node.init_node(self, outputs=[queue()])

        source = self.source if hasattr(self, 'source') else self
        node.init_node(node_instance,
                       inputs=self.outputs,
                       outputs=[queue()],
                       parent=self,
                       source=source)

        return node_instance

    return node_func

def register_source(source_class):
    """
    registers the source within flume and makes sure to setup any existing
    processors and sinks as chainable methods
    """
    if source_class.name in __SOURCES.keys():
        raise FlumineException('"%s" source already registered' % source_class.name)

    logger.debug('register_source %s', source_class.name)
    __SOURCES[source_class.name] = source_class

    for name in __PROCS.keys():
        setattr(source_class, name, build_node_func(__PROCS[name]))

    for sink_name in __SINKS.keys():
        setattr(source_class, sink_name, build_node_func(__SINKS[sink_name]))


def register_sink(sink_class):
    """
    registers the sink with flume and makes sure to hook itself up on any
    existing procs or sources as a chainable method
    """
    if sink_class.name in __SINKS.keys():
        raise FlumineException('"%s" sink already registered' % sink_class.name)

    logger.debug('register_sink %s', sink_class.name)
    __SINKS[sink_class.name] = sink_class

    for source in __SOURCES.values():
        setattr(source, sink_class.name, build_node_func(sink_class))

    for proc in __PROCS.values():
        setattr(proc, sink_class.name, build_node_func(sink_class))


def register_proc(proc_class):
    """
    registers the proc_class with flume and makes sure to hook any existing
    procs and sinks as chainable methods
    """
    if proc_class.name in __PROCS.keys():
        raise FlumineException('"%s" proc already registered' % proc_class.name)

    logger.debug('register_proc %s', proc_class.name)
    __PROCS[proc_class.name] = proc_class

    for source_class in __SOURCES.values():
        setattr(source_class, proc_class.name, build_node_func(proc_class))

    for other_proc_class in __PROCS.values():
        setattr(other_proc_class,
                proc_class.name,
                build_node_func(proc_class))
        setattr(proc_class,
                other_proc_class.name,
                build_node_func(other_proc_class))

    for sink_class in __SINKS.values():
        setattr(proc_class, sink.name, build_node_func(sink_class))

class node(object):
    """
    base flume node class
    """

    name = None

    EOF = Point(__eof=True)

    def __init__(self, *args, **kwargs):
        """
        the base node __init__ is just here to be record the arguments and
        keyword arguments used by each node
        """
        self.args = args
        self.kwargs = kwargs
        self.inited = True
        self.running = True
        self.exc_info = queue()
        self.inputs_index = None

    def init_node(self,
                  source=None,
                  parent=None,
                  inputs=None,
                  outputs=None):
        self.source = source
        self.inputs = inputs
        self.outputs = outputs
        self.parent = parent

    def pull(self, wait=True, timeout=None):
        """
        return a batch of points from the upstream procs and guarantee all
        points are sorted in order otherwise
        """
        times = []
        result = []

        if self.inputs is not None:

            if self.inputs_index is None:
                self.inputs_index = {}
                index = 0
                for input in self.inputs:
                    self.inputs_index[input] = index
                    index += 1

            for input in self.inputs:
                input_index = self.inputs_index[input]

                try:
                    points = input.get(wait)
                except Empty:
                    points = []

                for point in points:
                    point = Point(**point)

                    if point == self.EOF:
                        self.inputs.remove(input)
                        continue

                    point.__meta__.flume_path += ('.%s[%s]' % (self.name, input_index))

                    if 'time' not in point.keys():
                        result.append(point)

                    else:
                        index = bisect.bisect_left(times, point.time)
                        times.insert(index, point.time)
                        result.insert(index, point)

        if self.inputs is None or len(self.inputs) == 0:
            self.running = False

        logger.debug('%s pulling %s points', self, len(result))
        return result

    def push(self, points):
        """
        push the provided points to the outputs of this node so that other
        nodes downstream can receive it
        """

        if isinstance(points, Point):
            points = [points]

        logger.debug('%s pushing %s points', self, len(points))

        for point in points:
            for output in self.outputs:
                if point == self.EOF:
                    output.put([self.EOF])

                else:
                    output.put([Point(**point)])

    def __ror__(self, other):
        """

        """
        return node.__or__(splitter(flumes=other), self)

    def __or__(self, other):
        """
        enable the ability to use the bitwise or operator to emulate the pipe
        notation between flume nodes
        """
        if not hasattr(self, 'outputs'):
            node.init_node(self, outputs=[queue()])

        source = self.source if hasattr(self, 'source') else self

        if isinstance(other, tuple):
            # split the stream!
            other = splitter(flumes=list(other))

        node.init_node(other,
                       inputs=self.outputs,
                       outputs=[queue()],
                       parent=self,
                       source=source)
        return other

    def loop(self):
        """
        every node should implement a loop method which is where they can handle
        the pushing/pulling of points
        """
        raise FlumineException('Each node should implement the loop method')

    def run(self):
        """
        node run method used by flume internally to manage thread execution
        """
        try:
            self.loop()
            self.exc_info.put(None)

        except:
            self.exc_info.put(sys.exc_info())

        finally:
            # must make sure to push EOF even if there was a failure
            self.push([self.EOF])

    def execute(self,
                wait=True,
                loglevel=logger.WARN):

        if 'inited' not in self.__dict__ or not self.inited:
            raise FlumineException('node.__init__ was never used')

        # XXX: special case of a single source with no output doing an execute()
        #      on it shouldn't fail
        if not hasattr(self, 'outputs'):
            node.init_node(self, outputs=[])
        
        logger.setLogLevel(loglevel)

        # XXX: pooling here ?
        thread = threading.Thread(target=self.run)
        # Daemonize so that when we Ctrl+C the main program then all underlying
        # threads are instantly killed. Currently don't have any concern about
        # cleanly closing resources.
        thread.daemon = True
        thread.start()

        if self.parent:
            self.parent.execute(wait=wait, loglevel=loglevel)

        if wait:
            while thread.is_alive():
                # if you don't join with a timeout then you block the parent
                # until the child has completely finished and therefore can't
                # handle any signals in the parent (ie SIGINT)
                thread.join(1)

            exc_info = self.exc_info.get()

            if exc_info is not None:
                six.reraise(exc_info[0], exc_info[1], exc_info[2])

    def input_count(self):
        """
        returns how many inputs are currently hooked up to the current node
        """
        if self.parent.name == 'splitter':
            # XXX single point of hackery where we do something different for
            #     the split proc
            if len(self.parent.flumes) == 0:
                # since there's still the split input
                return 1

            else:
                return len(self.parent.flumes)
        else:
            return len(self.inputs)


class sink(node):
    """
    base sink class
    """

    def __init__(self, *args, **kwargs):
        node.__init__(self, *args, **kwargs)


class reducer(object):
    """
    base reducer class
    """

    def update(self, point):
        """
        update method called when there is a new point to be passed to the
        reducer
        """
        raise FlumineException('missing implementation for update method')

    def result(self):
        """
        reducer should return the reduced field value
        """
        raise FlumineException('missing implementation for result method')

class splitter(node):
    """
    # splitter

    The split processor is used internally to handle splitting the flume stream

    usage: ... | (put(...), filter(...), etc) | ...

    """

    name = 'splitter'

    def __init__(self,
                 flumes=None,
                 delay=None):
        node.__init__(self, flumes)
        self.flumes = flumes if flumes is not None else []

        if delay is not None:
            self.delay = moment.duration(delay)
        else:
            self.delay = moment.duration('5s')

        self.flume_outputs = []

    def loop(self):
        # self.input is None when split has no parent
        while self.running:
            points = self.pull()
            self.push(points)

    def execute(self,
                wait=True,
                loglevel=logging.ERROR):

        def find_root(flume):
            """
            figure out the root node of a flume pipeline
            """
            if hasattr(flume, 'parent') and \
               flume.parent is not None:
                return find_root(flume.parent)
            else:
                return flume

        if not hasattr(self, 'outputs'):
            node.init_node(self, outputs=[])

        if len(self.flumes) != 0:

            forwarder_inputs = self.outputs
            self.outputs = []

            for flume in self.flumes:
                flume_input = queue()
                root = find_root(flume)
                root.parent = None
                root.inputs = [flume_input]

                # don't setup the outputs for a sink as it will never
                # push anything out XXX: could be a bit more elegant
                if not isinstance(flume, sink):
                    output = queue()
                    self.flume_outputs.append(output)
                    flume.outputs = [output]

                self.outputs.append(flume_input)

            from flume.procs import reorder
            forwarder = reorder(delay=self.delay)

            source = self.source if hasattr(self, 'source') else self
            node.init_node(forwarder,
                           inputs=self.flume_outputs,
                           outputs=forwarder_inputs,
                           parent=None,
                           source=source)

            forwarder.execute(wait=False,
                              loglevel=loglevel)

            # start underlying flumes
            for flume in self.flumes:
                flume.execute(wait=False,
                              loglevel=loglevel)

        # override default behavior to execute the underlying flume
        node.execute(self,
                     wait=False,
                     loglevel=loglevel)
