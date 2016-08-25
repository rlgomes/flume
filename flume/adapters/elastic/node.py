"""
elastic adapter core module
"""

import json
import re

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import RequestError

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
                 time='time',
                 index='_all',
                 type='metric',
                 host='localhost',
                 port=9200,
                 filter=None,
                 batch=1024):
        self.time = time
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

        query = {
            'query': filter_to_es_query(self.filter)
        }

        if self.time is not None:
            query['sort'] = [self.time]

        logger.debug('es query %s' % json.dumps(query))

        try:
            for result in helpers.scan(client,
                                       index=self.index,
                                       query=query,
                                       preserve_order=True):
                point = Point(**result['_source'])
                points.append(point)

                if len(points) >= self.batch:
                    yield self.process_time_field(points, self.time)
                    points = []

            if len(points) > 0:
                yield self.process_time_field(points, self.time)

        except RequestError as exception:
            # make time field related errors a little easier to digest instead
            # of spewing the elasticsearch internal error which is a little less
            # human friendly
            error_type = exception.info['error']['type']
            if error_type == 'search_phase_execution_exception':
                reason = exception.info['error']['root_cause'][0]['reason']
                if re.match('No mapping found for .* in order to sort on',
                            reason):
                    raise FlumineException(
                        ('Time field "%s" not found in data, set time to ' +
                         'the appropriate value or None to query timeless ' +
                         'data') % self.time)

            raise

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
