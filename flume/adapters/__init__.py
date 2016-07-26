"""
adapters base module
"""

from flume.adapters.adapter import adapter
from flume.adapters.elastic import elastic
from flume.adapters.http import http
from flume.adapters.stdio import stdio
from flume.exceptions import FlumineException


_ADAPTERS = {}


def register_adapter(cls):
    """
    register a new adapter class
    """
    if cls.name in _ADAPTERS.keys():
        raise FlumineException('"%s" adapter already registered' % cls.name)

    _ADAPTERS[cls.name] = cls

def get_adapter(name, operation):
    """
    get a previously registered adapter class by name
    """
    if name not in _ADAPTERS.keys():
        raise FlumineException('"%s" adapter not registered' % name)

    result = _ADAPTERS[name]

    if getattr(result, operation) == getattr(adapter, operation):
        raise FlumineException('"%s" adapter does not support %s' %
                               (name, operation))

    return result
