"""
testing utilities
"""

import contextlib
import sys

from flume import logger

from dici import dici

__IS_PY2 = sys.version[0] == '2'

if __IS_PY2:
    from StringIO import StringIO

else:
    from io import StringIO


class FakeIO(object):

    def __init__(self, data=''):
        self.data = data

    def close(self):
        pass

    def flush(self):
        pass

    def read(self, size):
        result = self.data[:size]
        self.data = self.data[size:]
        return result

    def readline(self, limit=-1):
        index = self.data.find('\n')

        if index == -1 and len(self.data) != 0:
            result = self.data
            self.data = ''
            return result

        result = self.data[:index + 1]
        self.data = self.data[index + 1:]
        return result

    def readlines(self):
        while True:
            line = self.readline()

            if not line:
                break

            yield line

    def write(self, data):
        self.data += data

    def getvalue(self):
        return self.data

@contextlib.contextmanager
def redirect(input=''):
    """
    contextmanager to simply handle the redirection of stdout, stderr and
    intercept the sys.exit() call from running the CLI so the running Python
    instance doesn't exit but we can verify the exact exit code.
    """
    stdout = StringIO()
    stderr = StringIO()

    result = dici(exit=0,
                  stdout=None,
                  stderr=None)

    original_exit = sys.exit

    def exit(code):
        if result.stdout is None:
            result.stdout = stdout.getvalue()

        if result.stderr is None:
            result.stderr = stderr.getvalue()

        result.exit = code

    sys.exit = exit

    original_stdin = sys.stdin
    sys.stdin = FakeIO(input)

    original_stdout = sys.stdout
    sys.stdout = stdout

    original_stderr = sys.stderr
    sys.stderr = stderr

    logger.init()

    yield result

    sys.stdin = original_stdin
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    sys.exit = original_exit

    if result.stdout is None:
        result.stdout = stdout.getvalue()

    if result.stderr is None:
        result.stderr = stderr.getvalue()
