"""
streamers init module
"""
from flume.adapters.streamers.base import Streamer
from flume.adapters.streamers.csver import CSV
from flume.adapters.streamers.jsonler import JSONL
from flume.adapters.streamers.jsoner import JSON
from flume.adapters.streamers.grok import Grok
from flume.exceptions import FlumineException

_STREAMERS = {}


def get_streamer(name, *args, **kwargs):
    if name in _STREAMERS:
        return _STREAMERS[name](*args, **kwargs)

    else:
        raise FlumineException('"%s" streamer not registered' % name)

def register_streamer(name, streamer):
    if name in _STREAMERS.keys():
        raise FlumineException('"%s" streamer already registered' % name)

    _STREAMERS[name] = streamer

register_streamer('jsonl', JSONL)
register_streamer('json', JSON)
register_streamer('csv', CSV)
register_streamer('grok', Grok)
