"""
gnuplot unit tests
"""
import unittest
import mock

from bunch import Bunch
from robber import expect

from flume.sinks.views import PyGal
from flume import moment

from test.unit.util import FakeIO

def bar():
    class Bar(object):
        kwargs = None
        series = {}

        def __init__(self, **kwargs):
            Bar.kwargs = kwargs
            Bar.series = {}

        def add(self, series_name, data):
            Bar.series[series_name] = data

        def render_to_png(self, filename):
            pass
        
        def render(self):
            pass

    return Bar

class PyGalTest(unittest.TestCase):

    @mock.patch('sys.stdout', new_callable=FakeIO)
    @mock.patch('tempfile.mkstemp')
    @mock.patch('pygal.Bar', new_callable=bar)
    def test_can_render_a_simple_barchart_to_png(self,
                                                 mock_bar,
                                                 mock_mkstemp,
                                                 mock_sys_stdout):
        mock_mkstemp.return_value = (None, '/tmp/barchart.png')

        view = PyGal(height=100, width=200)
        view.render('barchart', {
            '2016': [('January', 10), ('Febuary', 20), ('April', 5)]
        })

        # we spam stdout with the indication we're writing out a file
        expect(mock_sys_stdout.getvalue()).to.eq('rendering chart to "/tmp/barchart.png"\n')
        # internal initialization of pygal.Bar
        expect(mock_bar.kwargs).to.eq({
            'height': 100,
            'width': 200
        })
        # various calls to add series
        expect(mock_bar.series).to.eq({
            '2016': [10, 20, 5]
        })


    @mock.patch('sys.stdout', new_callable=FakeIO)
    @mock.patch('tempfile.mkstemp')
    @mock.patch('pygal.Bar', new_callable=bar)
    def test_can_render_a_simple_barchart_to_html(self,
                                                  mock_bar,
                                                  mock_mkstemp,
                                                  mock_sys_stdout):
        mock_mkstemp.return_value = (None, '/tmp/barchart.html')

        view = PyGal(height=100, width=200, format='html')
        view.render('barchart', {
            '2016': [('January', 10), ('Febuary', 20), ('April', 5)]
        })

        # we spam stdout with the indication we're writing out a file
        expect(mock_sys_stdout.getvalue()).to.eq('rendering chart to "/tmp/barchart.html"\n')
        # internal initialization of pygal.Bar
        expect(mock_bar.kwargs).to.eq({
            'height': 100,
            'width': 200
        })
        # various calls to add series
        expect(mock_bar.series).to.eq({
            '2016': [10, 20, 5]
        })
