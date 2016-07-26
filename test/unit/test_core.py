import unittest

from robber import expect
from flume import *

from flume.core import register_sink, register_proc, register_source

class CoreTest(unittest.TestCase):
    """
    verifies basic flume flow behaviors
    """

    def test_failure_in_source_propagates_correctly(self):
        try:
            (
                emit(start=-1)
            ).execute()
        except Exception as exception:
            expect(exception.message).to.eq('Unable to parse moment "-1"')

    def test_failure_in_proc_propagates_correctly(self):

        class failme(reducer):

            def __init__(self):
                pass

            def update(self, point):
                raise Exception('failing on purpose')

        try:
            (
                emit(limit=10, start='2010-01-01')
                | put(foo=failme())
            ).execute()
        except Exception as exception:
            expect(exception.message).to.eq('failing on purpose')

    def test_failure_in_sink_propagates_correctly(self):

        try:
            (
                emit(limit=10, start='2010-01-01')
                | write('http', url='bananas')
            ).execute()
        except Exception as exception:
            expect(exception.message).to.contain('Invalid URL \'bananas\'')

    def test_register_existing_source_fails(self):
        try:
            register_source(emit)
        except FlumineException as exception:
            expect(exception).to.contain('"emit" source already registered')

    def test_register_existing_proc_fails(self):
        try:
            register_proc(put)
        except FlumineException as exception:
            expect(exception).to.contain('"put" proc already registered')

    def test_register_existing_sink_fails(self):
        try:
            register_sink(write)
        except FlumineException as exception:
            expect(exception).to.contain('"write" sink already registered')
