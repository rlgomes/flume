"""
elastic adapter core module
"""

import json

from elasticsearch import Elasticsearch, helpers

from flume import logger, moment
from flume.adapters.adapter import adapter
from flume.adapters.elastic.query import filter_to_es_query
from flume.exceptions import FlumineException
from flume.point import Point


class elastic(adapter):
    """
    elastic flume adapter
    """

    name = 'elastic'

    def __init__(self,
                 index='_all',
                 type='metric',
                 host='localhost',
                 port=9200,
                 filter=None,
                 batch=1024):
        self.index = index
        self.type = type
        self.host = host
        self.port = port
        self.filter = filter
        self.batch = batch
        self.clients = {}

    def _get_elasticsearch(self, host, port):
        """
        cache ES client
        """
        key = '%s:%s' % (host, port)

        if key not in self.clients:
            self.clients[key] = Elasticsearch([host], port=port)

        return self.clients[key]

    def read(self):
        """
        read points out of ES
        """
        points = []
        client = self._get_elasticsearch(self.host, self.port)

        query = filter_to_es_query(self.filter)
        logger.debug('es query %s' % json.dumps(query))

        for result in helpers.scan(client,
                                   index=self.index,
                                   query={'query': query, 'sort': ['time']},
                                   preserve_order=True):
            point = Point(**result['_source'])
            points.append(point)

            if len(points) > self.batch:
                yield points
                points = []

        if len(points) > 0:
            yield points

    def write(self, points):
        """
        write data points to the index in the ES instance indicated
        """
        client = self._get_elasticsearch(self.host, self.port)

        pushing = []

        for point in points:
            point = point.json()
            point['_index'] = self.index
            point['_type'] = self.type
            pushing.append(point)

        _, errors = helpers.bulk(client, pushing)

        for error in errors:
            logger.error(error)
            raise FlumineException('errors while writing to elasticsearch')

    def eof(self):
        pass
