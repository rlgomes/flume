"""
views unit tests
"""
import unittest
import mock

from flume import *
from flume.adapters.adapter import adapter
from flume.sinks import views

from robber import expect


class ViewsTest(unittest.TestCase):

    def test_can_not_find_unregistered_view(self):
        with self.assertRaisesRegexp(FlumineException,
                                     'view with name "bananas", not found'):
            views.get_view('bananas')

    def test_can_not_register_existing_view(self):
        views.register_view('existing-view', object)
        with self.assertRaisesRegexp(FlumineException,
                                     'view with name "existing-view", already registered'):
            views.register_view('existing-view', object)

    def test_can_get_registered_view(self):
        class dummy(object):
            pass

        views.register_view('registered-view', dummy)
        result = views.get_view('registered-view')

        expect(result).to.be.instanceof(dummy)
