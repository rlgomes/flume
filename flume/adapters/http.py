"""
http adapter
"""
import requests
import requests_cache

from flume import logger, moment
from flume.adapters.adapter import adapter
from flume.adapters import streamers
from flume.exceptions import FlumineException
from flume.point import Point


class RequestsStream(object):

    def __init__(self, response):
        self.response = response

    def read(self, size=1024):
        return self.response.iter_content(chunk_size=size)

    def readlines(self):
        tail = ''

        for data in self.read():
            data = tail + data
            lines = data.split('\n')

            head = lines[:-1]
            tail = lines[-1]

            for line in head:
                yield line

        for line in tail:
            yield line


class http(adapter):
    """
    http adapter
    """

    name = 'http'


    def __init__(self,
                 url=None,
                 method='GET',
                 headers=None,
                 follow_link=True,
                 format=None,
                 cache=None,
                 array=True,
                 status=[200],
                 **kwargs):
        self.url = url
        self.method = method
        self.headers = headers
        self.follow_link = follow_link
        self.cache = cache
        self.array = array

        if not isinstance(status, list):
            status = [status]

        self.status = status

        if format is not None:
            self.streamer = streamers.get_streamer(format, **kwargs)

        else:
            self.streamer = None

    def read(self):
        """
        read points by issuing an HTTP request and pushing the response as
        individual points into the flume pipeline
        """
        url = self.url

        while True:
            if self.cache is not None:
                requests_cache.install_cache(self.cache)

            def verify_response(response):
                if response.status_code not in self.status:
                    raise FlumineException('%s: %s' % (response.status_code, response.text))

            if self.streamer is not None:
                response = requests.request(self.method,
                                            url,
                                            headers=self.headers,
                                            stream=True)
                verify_response(response)
                data = self.streamer.read(RequestsStream(response))

            else:
                response = requests.request(self.method, url, headers=self.headers)
                verify_response(response)
                data = response.json()

            points = []
            for point in data:
                # convert to a flume Point
                point = Point(**point)
                points.append(point)

            yield points

            if not self.follow_link:
                break

            if 'link' in response.headers and 'next' in response.links:
                url = response.links['next']['url']

            else:
                break

    def __push(self, payload):
        response = requests.request(self.method,
                                    self.url,
                                    headers=self.headers,
                                    json=payload)

        if response.status_code not in self.status:
            raise FlumineException('received bad response with %d: %s' %
                                   (response.status_code, response.text))

    def write(self, points):
        if self.array:
            payload = []

            for point in points:
                payload.append(point.json())

            self.__push(payload)

        else:
            for point in points:
                self.__push(point.json())
