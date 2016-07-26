"""
http adapter
"""
import requests
import requests_cache

from flume import logger, moment
from flume.adapters.adapter import adapter
from flume.exceptions import FlumineException
from flume.point import Point


class http(adapter):
    """
    http adapter
    """

    name = 'http'

    def __init__(self,
                 url=None,
                 method='GET',
                 headers=None,
                 time='time',
                 filter=None,
                 follow_link=True,
                 cache=None):
        self.url = url
        self.method = method
        self.headers = headers
        self.time = time
        self.filter = filter
        self.follow_link = follow_link
        self.cache = cache

    def read(self):
        """
        read points by issuing an HTTP request and pushing the response as
        individual points into the flume pipeline
        """
        url = self.url

        while True:
            if self.cache is not None:
                requests_cache.install_cache(self.cache)

            response = requests.request(self.method, url, headers=self.headers)

            if response.status_code != 200:
                raise FlumineException(response.text)

            data = response.json()

            points = []
            for point in data:
                # convert to a flume Point
                point = Point(**point)

                if self.time in point:
                    point.time = moment.date(point[self.time])
                    points.append(point)

                else:
                    logger.warn('point missing time field "%s"' % self.time)

            yield points

            if not self.follow_link:
                break

            if 'link' in response.headers and 'next' in response.links:
                url = response.links['next']['url']

            else:
                break

    def write(self, points):
        payload = []
        for point in points:
            payload.append(point.json())

        if self.cache is not None:
            requests_cache.install_cache(self.cache)

        response = requests.request(self.method,
                                    self.url,
                                    headers=self.headers,
                                    json=payload)

        if response.status_code != 200:
            raise FlumineException('received bad response with %d: %s' %
                                   (response.status_code, response.text))

    def eof(self):
        pass
