"""
flume utilities
"""

import sys

IS_PY2 = sys.version[0] == '2'

def is_string(string):
    """
    check an object is a string across python 2 and 3
    """
    if IS_PY2:
        return isinstance(string, basestring)
    else:
        return isinstance(string, str)

def u(string):
    """
    return a string as a unicode string in python 2 and 3
    """
    if IS_PY2:
        return unicode(string)
    else:
        return str(string)
