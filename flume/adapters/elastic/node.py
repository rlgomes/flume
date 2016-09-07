"""
elastic adapter core module
"""

import json
import re

import elasticsearch

from elasticsearch import helpers
from elasticsearch.exceptions import RequestError

from flume import logger
from flume.adapters.adapter import adapter
from flume.adapters.elastic.query import filter_to_es_query
from flume.exceptions import FlumeException
from flume.point import Point


class elastic(adapter):
    """
    elastic flume adapter
    """

    name = 'elastic'

    def __init__(self,
                 time='time',
                 index=None,
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

        self.limit = None
        self.aggs = None

    def _get_elasticsearch(self, host, port):
        """
        cache ES client
        """
        key = '%s:%s' % (host, port)

        if key not in self.clients:
            self.clients[key] = elasticsearch.Elasticsearch([host], port=port)

        return self.clients[key]

    def optimize(self, proc):

        # head optimization
        if proc.name == 'head':
            self.limit = proc.howmany
            proc.remove_node()

        # reduce optimizations
        if proc.name == 'reduce':
            # currently only handling a single count reducer optimization
            if len(proc.fields) == 1:
                self.aggs = {}

                for (name, value) in proc.fields.items():
                    if value.name() == 'count':
                        # we can have es calculate this aggregation for us
                        self.aggs[name] = {
                            'value_count': {
                                'field': '_type'
                             }
                        }

                    elif value.name() == 'maximum':
                        # we can have es calculate this aggregation for us
                        self.aggs[name] = {
                            'max': {
                                'field': value.fieldname
                            }
                        }

                    elif value.name() == 'minimum':
                        # we can have es calculate this aggregation for us
                        self.aggs[name] = {
                            'min': {
                                'field': value.fieldname
                            }
                        }

                proc.remove_node()

    def read(self):
        """
        read points out of ES
        """
        points = []
        client = self._get_elasticsearch(self.host, self.port)

        try:
            if self.aggs is not None:
                query = {
                    'aggs': self.aggs,
                    # get the first result so we have a timestamp for our
                    # resulting reduction
                    'size': 1
                }

                if self.time is not None:
                    query['sort'] = [self.time]

                logger.debug('es query %s' % json.dumps(query))

                response = client.search(index=self.index or '_all',
                                         body=query)
                point = Point()

                for (name, nested_value) in response['aggregations'].items():
                    point[name] = nested_value['value']

                point[self.time] = response['hits']['hits'][0]['_source'][self.time]

                points.append(point)
                yield self.process_time_field(points, self.time)

            else:
                count = 0
                query = {
                    'query': filter_to_es_query(self.filter)
                }

                if self.time is not None:
                    query['sort'] = [self.time]

                logger.debug('es query %s' % json.dumps(query))

                for result in helpers.scan(client,
                                           index=self.index or '_all',
                                           query=query,
                                           preserve_order=True):
                    count += 1

                    point = Point(**result['_source'])
                    points.append(point)

                    if len(points) >= self.batch:
                        yield self.process_time_field(points, self.time)
                        points = []

                    if count == self.limit:
                        break

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
                    raise FlumeException(
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
            point['_index'] = self.index or 'metrics'
            point['_type'] = self.type
            pushing.append(point)

        _, errors = helpers.bulk(client, pushing)

        for error in errors:
            logger.error(error)
            raise FlumeException('errors while writing to elasticsearch')

    def eof(self):
        pass
