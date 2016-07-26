"""
http adapter unittests
"""

import threading
import time
import unittest

import json
import logging
import requests

from flask import Flask, request, Response
from robber import expect

from flume import *

# silence flask logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

_HOST = '0.0.0.0'
_PORT = 22222
_BASEURL = 'http://%s:%d' % (_HOST, _PORT)


class HTTPTestServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        class MyFlask(Flask):

            def __init__(self, *args, **kwargs):
                super(MyFlask, self).__init__(*args, **kwargs)
                self.db = {}

        app = MyFlask(__name__)

        @app.route('/empty')
        def empty():
            return Response('[]',
                            status=200,
                            mimetype='application/json')

        @app.route('/garbage')
        def garbage():
            return Response('garbage',
                            status=200,
                            mimetype='application/json')

        @app.route('/points')
        def points():
            page = int(request.args.get('page', '1'))
            count = int(request.args.get('count', '3'))
            start = request.args.get('start', 'now')
            every = request.args.get('every', '1s')

            start = moment.date(start)
            every = moment.duration(every)
            current_time = start

            result = []
            headers = {}

            if page > 1:
                link = '<%s/points?page=%d&count=%d>; rel="next"' % \
                       (_BASEURL, page - 1, count)
                headers['link'] = link

            for index in range(0, count):
                result.append({
                    'time': moment.datetime_to_iso8601(current_time)
                })
                current_time += every

            return Response(json.dumps(result),
                            status=200,
                            mimetype='application/json',
                            headers=headers)

        @app.route('/store', methods=['PUT', 'GET'])
        def store():
            key = request.args.get('key')

            if request.method == 'PUT':
                app.db[key] = json.loads(request.data)
                return Response(status=200)

            if request.method == 'GET':
                return Response(json.dumps(app.db[key]),
                                status=200,
                                mimetype='application/json')

        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            shutit = request.environ.get('werkzeug.server.shutdown')

            if shutit is None:
                raise RuntimeError('not running with the werkzeug server')

            shutit()

            return Response(status=200)

        try:
            app.run(host=_HOST, port=_PORT)
        except:
            # ignore failures at shutdown
            pass


class HttpTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPTestServer()
        cls.server.start()

        # wait for the server to come up
        # XXX: should set a timeout
        response = None
        while response is None or response.status_code != 200:
            time.sleep(0.1)
            try:
                response = requests.get(_BASEURL + '/empty')
            except:
                pass

    @classmethod
    def tearDownClass(cls):
        requests.post(_BASEURL + '/shutdown')

    def test_http_read_with_failure(self):
        results = []
        try:
            (
                read('http',
                     url=_BASEURL + '/garbage')
                | memory(results)
            ).execute()

            raise Exception('previous code should have failed')
        except ValueError as exception:
            expect(exception.message).to.eq('No JSON object could be decoded')
            expect(results).to.eq([])

    def test_empty_http_read(self):
        results = []
        (
            read('http',
                 url=_BASEURL + '/empty')
            | memory(results)
        ).execute()
        expect(results).to.eq([])

    def test_http_read_a_few_historical_points(self):
        results = []
        (
            read('http',
                 url=_BASEURL + '/points?count=3&start=2010-01-01')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2010-01-01T00:00:00.000Z'},
            {'time': '2010-01-01T00:00:01.000Z'},
            {'time': '2010-01-01T00:00:02.000Z'}
        ])

    def test_http_read_a_few_live_points(self):
        results = []
        (
            read('http',
                 url=_BASEURL + '/points?count=5')
            | memory(results)
        ).execute()

        expect(results).to.have.length(5)

    def test_http_write_a_point_and_read_it_back(self):
        results = []
        (
            emit(limit=1, start='1970-01-01')
            | put(foo='bar')
            | write('http',
                    method='PUT',
                    url=_BASEURL + '/store?key=test1')
        ).execute()

        (
            read('http',
                 method='GET',
                 url=_BASEURL + '/store?key=test1')
            | keep('foo')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'foo': 'bar'}])

    def test_http_write_a_single_payload_and_read_them_back(self):
        results = []
        (
            emit(limit=3, start='1970-01-01')
            | put(count=count())
            | write('http',
                    method='PUT',
                    url=_BASEURL + '/store?key=test2',
                    batch=3)
        ).execute()

        (
            read('http',
                 method='GET',
                 url=_BASEURL + '/store?key=test2')
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

    def test_http_write_multiple_payloads_and_read_them_back(self):
        results = []
        (
            emit(limit=3, start='1970-01-01')
            | put(count=count())
            | write('http',
                    method='PUT',
                    url=_BASEURL + '/store?key=test2',
                    batch=1)
        ).execute()

        (
            read('http',
                 method='GET',
                 url=_BASEURL + '/store?key=test2')
            | keep('count')
            | memory(results)
        ).execute()

        # because the payload is of a single point we only end up storing the
        # last point that was pushed
        expect(results).to.eq([
            {'count': 3}
        ])

    def test_http_read_can_follow_link_header(self):
        results = []
        (
            read('http',
                 method='GET',
                 url=_BASEURL + '/points?count=2&page=3')
            | reduce(count=count())
            | keep ('count')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'count': 6}])
