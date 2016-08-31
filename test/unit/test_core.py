import unittest

from robber import expect
from flume import *
from flume.exceptions import FlumeException

from flume.core import register_sink, register_proc, register_source

class CoreTest(unittest.TestCase):
    """
    verifies basic flume flow behaviors
    """

    def test_remove_node_works_in_the_middle_of_the_pipeline(self):
        results = []

        a = emit(limit=3, start='2016-01-01')
        b = put(foo='bar')
        c = memory(results)

        pipeline = a | b | c
        # by removing the node it should no longer annotate the output with the
        # field foo='bar'
        b.remove_node()
        pipeline.execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z'},
            {'time': '2016-01-01T00:00:01.000Z'},
            {'time': '2016-01-01T00:00:02.000Z'}
        ])

    def test_remove_node_works_on_end_of_pipeline(self):
        results = []

        a = emit(limit=3, start='2016-01-01')
        b = put(foo='bar')
        c = memory(results)

        pipeline = a | b | c
        c.remove_node()
        pipeline.execute()

        expect(results).to.eq([])

    def test_failure_in_source_propagates_correctly(self):
        with self.assertRaisesRegexp(FlumeException, 'Unable to parse moment "-1"'):
            (
                emit(start=-1)
            ).execute()

    def test_failure_in_proc_propagates_correctly(self):
        class failme(reducer):

            def __init__(self):
                pass

            def update(self, point):
                raise Exception('failing on purpose')

        with self.assertRaisesRegexp(Exception, 'failing on purpose'):
            (
                emit(limit=10, start='2010-01-01')
                | put(foo=failme())
            ).execute()

    def test_failure_in_sink_propagates_correctly(self):
        with self.assertRaisesRegexp(Exception, 'Invalid URL \'bananas\''):
            (
                emit(limit=10, start='2010-01-01')
                | write('http', url='bananas')
            ).execute()

    def test_register_existing_source_fails(self):
        with self.assertRaisesRegexp(FlumeException, '"emit" source already registered'):
            register_source(emit)

    def test_register_existing_proc_fails(self):
        with self.assertRaisesRegexp(FlumeException, '"put" proc already registered'):
            register_proc(put)

    def test_register_existing_sink_fails(self):
        with self.assertRaisesRegexp(FlumeException, '"write" sink already registered'):
            register_sink(write)
