"""
processor init module
"""
from flume.procs.keep import keep
from flume.procs.remove import remove
from flume.procs.put import put
from flume.procs.head import head
from flume.procs.tail import tail

# pylint: disable=redefined-builtin
from flume.procs.filter import filter

# pylint: disable=redefined-builtin
from flume.procs.reduce import reduce

from flume.procs.seq import seq

from flume.procs.reorder import reorder
from flume.procs.sort import sort

# set procs
from flume.procs.diff import diff
from flume.procs.intersect import intersect
from flume.procs.union import union
