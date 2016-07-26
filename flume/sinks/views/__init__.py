"""
"""
from flume.exceptions import FlumineException

_VIEWS = {}

def get_view(name, **kwargs):
    if name not in _VIEWS:
        raise FlumineException('view with name "%s", not found' % name)

    return _VIEWS[name](**kwargs)

def register_view(name, view):
    if name in _VIEWS:
        raise FlumineException('view with name "%s", already registered' % name)

    _VIEWS[name] = view

from flume.sinks.views.pygalview import PyGal
from flume.sinks.views.gnuplot import Gnuplot

register_view('pygal', PyGal)
register_view('gnuplot', Gnuplot)
