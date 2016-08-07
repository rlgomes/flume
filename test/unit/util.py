"""
testing utilities
"""

import sys

__IS_PY2 = sys.version[0] == '2'


if __IS_PY2:
    from StringIO import StringIO
else:
    from io import StringIO

