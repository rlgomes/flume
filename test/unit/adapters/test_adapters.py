"""
base adapter unittests
"""

import unittest

from flume.adapters import register_adapter, get_adapter
from flume.adapters import adapter
from flume.exceptions import FlumineException

from robber import expect


class AdaptersTest(unittest.TestCase):

    def test_register_non_unique_adapter_fails(self):
        class TestAdapter(adapter):
            name = 'non-unique'

        register_adapter(TestAdapter)
        try:
            register_adapter(TestAdapter)
            raise Exception('previous statement should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('"non-unique" adapter already registered')

    def test_register_and_get_adapter_by_name(self):
        class TestAdapter(adapter):
            name = 'another'

            def read(self, stream):
                pass

        register_adapter(TestAdapter)
        result = get_adapter('another', 'read')
        expect(result).to.eq(TestAdapter)

    def test_get_adapter_of_inexistent_adapter_fails(self):
        try:
            get_adapter('non-existent', 'read')
            raise Exception('previous statement should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('"non-existent" adapter not registered')

    def test_register_and_get_adapter_by_name_with_missing_operation_fails(self):
        class TestAdapter(adapter):
            name = 'not-writable'

        register_adapter(TestAdapter)
        try:
            get_adapter('not-writable', 'write')
        except FlumineException as exception:
            expect(exception.message).to.contain('"not-writable" adapter does not support write')
