"""
flume init module

- place to define what gets exported from the flume package and how
"""

import flume.logger as logger

from flume.point import Point

from flume.adapters import adapter, \
                           elastic, \
                           http, \
                           stdio, \
                           register_adapter, \
                           get_adapter

from flume.core import node, \
                       queue, \
                       reducer, \
                       sink, \
                       register_source, \
                       register_proc, \
                       register_sink

from flume.thirdparty import *

from flume.exceptions import *

from flume.moment import *
from flume.sources import *
from flume.procs import *
from flume.procs import *
from flume.sinks import *

from flume.procs.reduce.reducers import *

"""
register built in sources, procs, sinks, etc of flume
"""

register_source(emit)
register_source(read)

register_proc(intersect)
register_proc(keep)
register_proc(put)
register_proc(head)
register_proc(tail)
register_proc(reduce)
register_proc(remove)
register_proc(reorder)
register_proc(sort)
register_proc(union)

register_sink(memory)
register_sink(write)

register_sink(barchart)
register_sink(linechart)

register_adapter(http)
register_adapter(elastic)
register_adapter(stdio)
