"""
base streamer unittests
"""

import unittest

from robber import expect

from flume.adapters.streamers import Streamer, register_streamer, get_streamer
from flume.exceptions import FlumineException
from test.unit.util import FakeIO


class BaseStreamersTest(unittest.TestCase):

    def test_register_non_unique_streamer_fails(self):
        register_streamer('non-unique', object())
        try:
            register_streamer('non-unique', object())
            raise Exception('previous statement should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('"non-unique" streamer already registered')

    def test_register_and_get_streamer_by_name(self):
        class TestStreamer(Streamer):

            def __init__(self):
                pass

        register_streamer('another', TestStreamer)
        result = get_streamer('another')
        self.assertIsInstance(result, TestStreamer)

    def test_get_streamer_of_inexistent_streamer_fails(self):
        try:
            get_streamer('non-existent')
            raise Exception('previous statement should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('"non-existent" streamer not registered')

    def test_new_streamer_must_have_a_read_method(self):
        try:
            class TestStreamer(Streamer):
                def __init__(self):
                    pass

            stream = FakeIO()
            streamer = TestStreamer()
            streamer.read(stream)
            raise Exception('previous statement should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('you must implement the read method')

    def test_new_streamer_must_have_a_write_method(self):
        try:
            class TestStreamer(Streamer):
                def __init__(self):
                    pass

            stream = FakeIO()
            streamer = TestStreamer()
            streamer.write(stream, [])
            raise Exception('previous statement should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('you must implement the write method')
