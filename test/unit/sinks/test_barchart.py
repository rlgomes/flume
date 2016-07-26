"""
barchart unit tests
"""
import unittest
import mock

from flume import *
from flume import moment
from flume.adapters.adapter import adapter

from robber import expect


class BarchartTest(unittest.TestCase):

    @mock.patch('flume.sinks.views.gnuplot.Gnuplot.render')
    def test_can_handle_an_empty(self, mock_render):
        (
            emit(points=[])
            | barchart('gnuplot')
        ).execute()
        expect(mock_render.call_args).to.eq(mock.call('barchart', {}))

    @mock.patch('flume.sinks.views.gnuplot.Gnuplot.render')
    def test_can_handle_a_single_series(self, mock_render):
        (
            emit(points=[
                {'time': '2016-01-01T00:00:01.000Z', 'name': 'series1', 'value': 1},
                {'time': '2016-01-01T00:00:02.000Z', 'name': 'series1', 'value': 2},
                {'time': '2016-01-01T00:00:03.000Z', 'name': 'series1', 'value': 3}
            ])
            | barchart('gnuplot')
        ).execute()
        expect(mock_render.call_args).to.eq(mock.call('barchart', {
            'series1': [
                (moment.date('2016-01-01T00:00:01.000Z'), 1),
                (moment.date('2016-01-01T00:00:02.000Z'), 2),
                (moment.date('2016-01-01T00:00:03.000Z'), 3)
            ]
        }))

    @mock.patch('flume.sinks.views.gnuplot.Gnuplot.render')
    def test_can_handle_multiple_series(self, mock_render):
        (
            emit(points=[
                {'time': '2016-01-01T00:00:01.000Z', 'name': 'series1', 'value': 1},
                {'time': '2016-01-01T00:00:02.000Z', 'name': 'series2', 'value': 2},
                {'time': '2016-01-01T00:00:03.000Z', 'name': 'series1', 'value': 3},
                {'time': '2016-01-01T00:00:04.000Z', 'name': 'series2', 'value': 4},
                {'time': '2016-01-01T00:00:05.000Z', 'name': 'series1', 'value': 5},
                {'time': '2016-01-01T00:00:06.000Z', 'name': 'series2', 'value': 6}
            ])
            | barchart('gnuplot')
        ).execute()
        expect(mock_render.call_args).to.eq(mock.call('barchart', {
            'series1': [
                (moment.date('2016-01-01T00:00:01.000Z'), 1),
                (moment.date('2016-01-01T00:00:03.000Z'), 3),
                (moment.date('2016-01-01T00:00:05.000Z'), 5)
            ],
            'series2': [
                (moment.date('2016-01-01T00:00:02.000Z'), 2),
                (moment.date('2016-01-01T00:00:04.000Z'), 4),
                (moment.date('2016-01-01T00:00:06.000Z'), 6)
           ]
        }))

    @mock.patch('flume.logger.warn')
    @mock.patch('flume.sinks.views.gnuplot.Gnuplot.render')
    def test_can_handle_a_series_with_no_series_field_and_no_other_tags(self, mock_render, mock_warn):
        (
            emit(points=[
                {'time': '2016-01-01T00:00:01.000Z', 'value': 1},
                {'time': '2016-01-01T00:00:02.000Z', 'value': 2},
                {'time': '2016-01-01T00:00:03.000Z', 'value': 3}
            ])
            | barchart('gnuplot')
        ).execute()
        expect(mock_render.call_args).to.eq(mock.call('barchart', {
            'unknown': [
                (moment.date('2016-01-01T00:00:01.000Z'), 1),
                (moment.date('2016-01-01T00:00:02.000Z'), 2),
                (moment.date('2016-01-01T00:00:03.000Z'), 3)
            ]
        }))
        expect(mock_warn.call_args_list).to.eq([
            mock.call('unable to find series field "name" in point'),
            mock.call('unable to find series field "name" in point'),
            mock.call('unable to find series field "name" in point')
        ])

    @mock.patch('flume.logger.warn')
    @mock.patch('flume.sinks.views.gnuplot.Gnuplot.render')
    def test_can_handle_a_series_with_no_series_field_but_with_other_tags(self, mock_render, mock_warn):
        (
            emit(points=[
                {'time': '2016-01-01T00:00:01.000Z', 'value': 1, 'series': 1},
                {'time': '2016-01-01T00:00:02.000Z', 'value': 2, 'series': 1},
                {'time': '2016-01-01T00:00:03.000Z', 'value': 3, 'series': 1}
            ])
            | barchart('gnuplot')
        ).execute()
        expect(mock_render.call_args).to.eq(mock.call('barchart', {
            'unknown': [
                (moment.date('2016-01-01T00:00:01.000Z'), 1),
                (moment.date('2016-01-01T00:00:02.000Z'), 2),
                (moment.date('2016-01-01T00:00:03.000Z'), 3)
            ]
        }))
        expect(mock_warn.call_args_list).to.eq([
            mock.call('unable to find series field "name" in point'),
            mock.call('unable to find series field "name" in point'),
            mock.call('unable to find series field "name" in point')
        ])
