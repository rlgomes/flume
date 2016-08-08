"""
http adapter unittests
"""

import threading
import time
import unittest

import json
import mock
import requests

from dici import dici
from robber import expect

from flume import *
from flume import moment

class HttpTest(unittest.TestCase):

    @mock.patch('requests.request')
    def test_http_read_with_expected_400_status(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'Bad Request',
            'headers': [],
            'json': lambda: []
        })

        (
            read('http',
                 url='http://localhost:8080/fail',
                 status=400)
        ).execute()

    @mock.patch('requests.request')
    def test_http_write_with_expected_400_status(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'Bad Request',
            'headers': [],
            'json': lambda: []
        })

        (
            emit(limit=1)
            | write('http',
                 url='http://localhost:8080/fail',
                 status=400)
        ).execute()

    @mock.patch('requests.request')
    def test_http_read_with_bad_http_response(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 500,
            'text': 'Internal Server Error',
            'headers': []
        })

        try:
            (
                read('http',
                     url='http://localhost:8080/fail')
            ).execute()

            raise Exception('previous code should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('Internal Server Error')

        expect(mock_request.call_args_list).to.eq([
            mock.call('GET', 'http://localhost:8080/fail', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_read_with_failure(self, mock_request):
        
        def raise_json_failure():
            raise ValueError('No JSON object could be decoded')

        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {
                'content-type': 'application/json'
            },
            'json': raise_json_failure
        })

        results = []
        try:
            (
                read('http',
                     url='http://localhost:8080/garbage')
                | memory(results)
            ).execute()

            raise Exception('previous code should have failed')
        except ValueError as exception:
            expect(str(exception)).to.eq('No JSON object could be decoded')
            expect(results).to.eq([])

        expect(mock_request.call_args_list).to.eq([
            mock.call('GET', 'http://localhost:8080/garbage', headers=None)
        ])

    @mock.patch('requests.request')
    def test_empty_http_read(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {
                'content-type': 'application/json'
            },
            'json': lambda: json.loads('[]')
        })

        results = []
        (
            read('http',
                 url='http://localhost:8080/empty')
            | memory(results)
        ).execute()
        expect(results).to.eq([])

        expect(mock_request.call_args_list).to.eq([
            mock.call('GET', 'http://localhost:8080/empty', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_read_a_few_historical_points(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {
                'content-type': 'application/json'
            },
            'json': lambda: [
                {'time': '2010-01-01T00:00:00.000Z'},
                {'time': '2010-01-01T00:00:01.000Z'},
                {'time': '2010-01-01T00:00:02.000Z'}
            ]
        })

        results = []
        (
            read('http',
                 url='http://localhost:8080/points?count=3&start=2010-01-01')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2010-01-01T00:00:00.000Z'},
            {'time': '2010-01-01T00:00:01.000Z'},
            {'time': '2010-01-01T00:00:02.000Z'}
        ])

        expect(mock_request.call_args_list).to.eq([
            mock.call('GET', 'http://localhost:8080/points?count=3&start=2010-01-01', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_read_a_few_live_points(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {
                'content-type': 'application/json'
            },
            'json': lambda: [
                {'time': moment.now()},
                {'time': moment.now()},
                {'time': moment.now()},
                {'time': moment.now()},
                {'time': moment.now()}
            ]
        })

        results = []
        (
            read('http',
                 url='http://localhost:8080/points?count=5')
            | memory(results)
        ).execute()

        expect(results).to.have.length(5)

        expect(mock_request.call_args_list).to.eq([
            mock.call('GET', 'http://localhost:8080/points?count=5', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_write_with_bad_http_response(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 500,
            'text': 'Internal Server Error',
        })

        results = []
        try:
            (
                emit(limit=1, start='2016-01-01')
                | write('http', url='http://localhost:8080/fail')
            ).execute()

            raise Exception('previous code should have failed')
        except FlumineException as exception:
            expect(exception.message).to.contain('Internal Server Error')

        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'http://localhost:8080/fail',
                      headers=None,
                      json=[{'time': '2016-01-01T00:00:00.000Z'}])
        ])

    @mock.patch('requests.request')
    def test_http_write_a_point_and_read_it_back(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {}
        })

        results = []
        (
            emit(limit=1, start='1970-01-01')
            | put(foo='bar')
            | write('http',
                    method='PUT',
                    url='http://localhost:8080/store?key=test1')
        ).execute()

        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {},
            'json': lambda: [{'time': '1970-01-01T00:00:00.000Z', 'foo': 'bar'}]
        })

        (
            read('http',
                 method='GET',
                 url='http://localhost:8080/store?key=test1')
            | keep('foo')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'foo': 'bar'}])

        expect(mock_request.call_args_list).to.eq([
            mock.call('PUT',
                      'http://localhost:8080/store?key=test1',
                      headers=None,
                      json=[{'time': '1970-01-01T00:00:00.000Z', 'foo': 'bar'}]),
            mock.call('GET', 'http://localhost:8080/store?key=test1', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_write_a_single_payload_and_read_them_back(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {}
        })

        results = []
        (
            emit(limit=3, start='1970-01-01')
            | put(count=count())
            | write('http',
                    method='PUT',
                    url='http://localhost:8080/store?key=test2',
                    batch=3)
        ).execute()

        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {},
            'json': lambda: [
                {'time': '1970-01-01T00:00:00.000Z', 'count': 1},
                {'time': '1970-01-01T00:00:01.000Z', 'count': 2},
                {'time': '1970-01-01T00:00:02.000Z', 'count': 3}
            ]
        })

        (
            read('http',
                 method='GET',
                 url='http://localhost:8080/store?key=test2')
            | keep('count')
            | memory(results)
        ).execute()

        # if we wrote out multiple paylaods then the end result would be that
        # we would only be able to retrieve the last point
        expect(results).to.eq([
            {'count': 1},
            {'count': 2},
            {'count': 3}
        ])

        expect(mock_request.call_args_list).to.eq([
            mock.call('PUT',
                      'http://localhost:8080/store?key=test2',
                      headers=None,
                      json=[
                          {'time': '1970-01-01T00:00:00.000Z', 'count': 1},
                          {'time': '1970-01-01T00:00:01.000Z', 'count': 2},
                          {'time': '1970-01-01T00:00:02.000Z', 'count': 3}
                      ]),
            mock.call('GET', 'http://localhost:8080/store?key=test2', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_write_multiple_payloads_and_read_them_back(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {}
        })

        results = []
        (
            emit(limit=3, start='1970-01-01')
            | put(count=count())
            | write('http',
                    method='PUT',
                    url='http://localhost:8080/store?key=test2',
                    batch=1)
        ).execute()

        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {},
            'json': lambda: [
                {'time': '1970-01-01T00:00:00.000Z', 'count': 3}
            ]
        })

        (
            read('http',
                 method='GET',
                 url='http://localhost:8080/store?key=test2')
            | keep('count')
            | memory(results)
        ).execute()

        # because the payload is of a single point we only end up storing the
        # last point that was pushed
        expect(results).to.eq([
            {'count': 3}
        ])

        expect(mock_request.call_args_list).to.eq([
            mock.call('PUT',
                      'http://localhost:8080/store?key=test2',
                      headers=None,
                      json=[{'time': '1970-01-01T00:00:00.000Z', 'count': 1}]),
            mock.call('PUT',
                      'http://localhost:8080/store?key=test2',
                      headers=None,
                      json=[{'time': '1970-01-01T00:00:01.000Z', 'count': 2}]),
            mock.call('PUT',
                      'http://localhost:8080/store?key=test2',
                      headers=None,
                      json=[{'time': '1970-01-01T00:00:02.000Z', 'count': 3}]),
            mock.call('GET', 'http://localhost:8080/store?key=test2', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_write_single_points(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': {}
        })

        (
            emit(limit=3, start='1970-01-01')
            | put(count=count())
            | write('http',
                    method='PUT',
                    url='http://localhost:8080/store?key=test2',
                    array=False)
        ).execute()

        expect(mock_request.call_args_list).to.eq([
            mock.call('PUT',
                      'http://localhost:8080/store?key=test2',
                      headers=None,
                      json={'time': '1970-01-01T00:00:00.000Z', 'count': 1}),
            mock.call('PUT',
                      'http://localhost:8080/store?key=test2',
                      headers=None,
                      json={'time': '1970-01-01T00:00:01.000Z', 'count': 2}),
            mock.call('PUT',
                      'http://localhost:8080/store?key=test2',
                      headers=None,
                      json={'time': '1970-01-01T00:00:02.000Z', 'count': 3}),
        ])

    @mock.patch('requests.request')
    def test_http_read_can_follow_link_header(self, mock_request):
        points = [
            {'time': '2016-01-01T00:00:00.000Z'},
            {'time': '2016-01-01T00:00:01.000Z'}
        ]
        mock_request.side_effect = [
            dici(**{
                'status_code': 200,
                'text': 'OK',
                'headers': {
                    'link': '<http://localhost:8080/?count=2&page=2>; rel="next"'
                },
                'links': {
                    'next': {
                        'url': 'http://localhost:8080/points?count=2&page=2'
                    }
                },
                'json': lambda: points
            }),
            dici(**{
                'status_code': 200,
                'text': 'OK',
                'headers': {
                    'link': '<http://localhost:8080/?count=2&page=1>; rel="next"'
                },
                'links': {
                    'next': {
                        'url': 'http://localhost:8080/points?count=2&page=1'
                    }
                },
                'json': lambda: points
            }),
            dici(**{
                'status_code': 200,
                'text': 'OK',
                'links': {},
                'headers': {},
                'json': lambda: points
            }),
        ]

        results = []
        (
            read('http',
                 method='GET',
                 url='http://localhost:8080/points?count=2&page=3')
            | reduce(count=count())
            | keep('count')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'count': 6}])

        expect(mock_request.call_args_list).to.eq([
            mock.call('GET', 'http://localhost:8080/points?count=2&page=3', headers=None),
            mock.call('GET', 'http://localhost:8080/points?count=2&page=2', headers=None),
            mock.call('GET', 'http://localhost:8080/points?count=2&page=1', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_read_can_not_follow_link_header(self, mock_request):
        points = [
            {'time': '2016-01-01T00:00:00.000Z'},
            {'time': '2016-01-01T00:00:01.000Z'}
        ]
        mock_request.side_effect = [
            dici(**{
                'status_code': 200,
                'text': 'OK',
                'headers': {
                    'link': '<http://localhost:8080/?page=2&count=2>; rel="next"'
                },
                'links': {
                    'next': {
                        'url': 'http://localhost:8080/points?page=2&count=2'
                    }
                },
                'json': lambda: points
            }),
            dici(**{
                'status_code': 200,
                'text': 'OK',
                'headers': {
                    'link': '<http://localhost:8080/?page=1&count=2>; rel="next"'
                },
                'links': {
                    'next': {
                        'url': 'http://localhost:8080/points?page=1&count=2'
                    }
                },
                'json': lambda: points
            }),
            dici(**{
                'status_code': 200,
                'text': 'OK',
                'links': {},
                'headers': {},
                'json': lambda: points
            }),
        ]

        results = []
        (
            read('http',
                 method='GET',
                 url='http://localhost:8080/points?count=2&page=3',
                 follow_link=False)
            | reduce(count=count())
            | keep('count')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'count': 2}])

        expect(mock_request.call_args_list).to.eq([
            mock.call('GET', 'http://localhost:8080/points?count=2&page=3', headers=None)
        ])

    @mock.patch('requests.request')
    def test_http_read_can_handle_grok_format_corectly(self, mock_request):
        with open('examples/grok/syslog') as syslog:
            mock_request.return_value = dici(**{
                'status_code': 200,
                'iter_content': lambda chunk_size: syslog.readlines(),
                'headers': []
            })

            results = []
            (
                read('http',
                     method='GET',
                     url='http://localhost:8080/syslog',
                     format='grok',
                     pattern='%{SYSLOGLINE}')
                | reduce(count=count())
                | keep('count')
                | memory(results)
            ).execute()

            expect(results).to.eq([{'count': 274}])
            expect(mock_request.call_args_list).to.eq([
                mock.call('GET', 'http://localhost:8080/syslog', headers=None, stream=True)
            ])
