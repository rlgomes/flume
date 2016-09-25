"""
elastic adapter query conversion unittests
"""
import unittest
import mock

from robber import expect
from elasticsearch.exceptions import RequestError
from flume.exceptions import FlumeException

from flume import *


class ElasticTest(unittest.TestCase):

    @mock.patch('elasticsearch.Elasticsearch')
    def test_read_can_handle_custom_host_and_port(self, mock_elastic):
        mock_elastic.return_value = mock.MagicMock(**{
            'search.return_value': {
                'hits': {
                    'total': 0
                }
            }
        })

        read('elastic', host='localhost', port=9999).execute()
        expect(mock_elastic.call_args).to.eq(mock.call(['localhost'], port=9999))

    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.Elasticsearch.search')
    def test_read_reports_nicer_exception_on_mapping_issue(self, mock_search, mock_elastic):
        mock_elastic.return_value = mock.MagicMock(**{
            'search.side_effect': RequestError(400, 'oh doh', {
                'error': {
                    'type': 'search_phase_execution_exception',
                    'root_cause': [
                        {
                            'reason': 'No mapping found for [time] in order to sort on'
                        }
                    ]
                }
            })
        })

        with self.assertRaisesRegexp(FlumeException,
                                     'Time field "time" not found in data, ' +
                                     'set time to the appropriate value or ' +
                                     'None to query timeless data'):
            read('elastic').execute()

    @mock.patch('elasticsearch.Elasticsearch')
    def test_read_reports_exceptions_on_non_mapping_issue(self, mock_elastic):
        mock_elastic.return_value = mock.MagicMock(**{
            'search.side_effect': RequestError(400, 'oh doh', {
                'error': {
                    'type': 'some_other_phase_execution_exception'
                }
            })
        })

        with self.assertRaisesRegexp(RequestError, 'oh doh'):
            read('elastic').execute()

    @mock.patch('elasticsearch.Elasticsearch')
    def test_read_can_handle_empty_response(self, mock_elastic):
        elastic = mock.MagicMock(**{
            'search.return_value': {
                'hits': {
                    'total': 0
                }
            }
        })
        mock_elastic.return_value = elastic
        results = []

        (read('elastic') | memory(results)).execute()

        expect(results).to.eq([])
        expect(elastic.search.call_args).to.eq(
            mock.call(body={
                'sort': ['time'],
                'query': {
                    'match_all': {}
                }
            },
            index='_all',
            scroll='5m'))

    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_handle_a_single_timeless_point(self,
                                                     mock_scan,
                                                     mock_elastic):
        mock_elastic.return_value = mock.MagicMock()
        mock_scan.return_value = [
            { '_source': { 'foo': 'bar' } }
        ]
        results = []

        (read('elastic') | memory(results)).execute()

        expect(results).to.eq([{'foo': 'bar'}])
        expect(mock_scan.call_args).to.eq(
            mock.call(mock_elastic.return_value,
                      index='_all',
                      preserve_order=True,
                      query={
                          'sort': ['time'],
                          'query': {
                              'match_all': {}
                          }
                      }))


    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_handle_a_single_point_with_time(self,
                                                      mock_scan,
                                                      mock_elastic):
        mock_elastic.return_value = mock.MagicMock()
        mock_scan.return_value = [
            {
                '_source': {
                    'time': '2016-01-01T00:00:00.000Z',
                    'foo': 'bar'
                }
            }
        ]
        results = []

        (read('elastic') | memory(results)).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'foo': 'bar'}
        ])
        expect(mock_scan.call_args).to.eq(
            mock.call(mock_elastic.return_value,
                      index='_all',
                      preserve_order=True,
                      query={
                          'sort': ['time'],
                          'query': {
                              'match_all': {}
                          }
                      }))

    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_read_from_a_specific_index(self, mock_scan, mock_elastic):
        mock_elastic.return_value = mock.MagicMock()
        mock_scan.return_value = [
            {'_source': {'foo': 'bar'}}
        ]
       
        results = []
        (read('elastic', index='foo') | memory(results)).execute()

        expect(results).to.eq([{'foo': 'bar'}])
        expect(mock_scan.call_args).to.eq(
            mock.call(mock_elastic.return_value,
                      index='foo',
                      preserve_order=True,
                      query={
                          'sort': ['time'],
                          'query': {
                              'match_all': {}
                          }
                      }))

    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_read_with_filter(self, mock_scan, mock_elastic):
        mock_elastic.return_value = mock.MagicMock()
        mock_scan.return_value = [
            {'_source': {'foo': 'bar'}}
        ]
 
        mock_elastic.return_value = elastic
        results = []
        (
            read('elastic', index='foo', filter='count > 3')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'foo': 'bar'}])
        query = {
            'sort': ['time'],
            'query': {
                'constant_score': {
                    'filter': {
                        'range': {
                            'count': {
                                'gt': 3
                            }
                        }
                    }
                }
            }
        }

        expect(mock_scan.call_args).to.eq(
            mock.call(mock_elastic.return_value,
                      index='foo',
                      preserve_order=True,
                      query=query))

    @mock.patch('flume.sources.read.push')
    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_abides_by_batch_size(self, mock_scan, mock_elastic, mock_push):
        mock_scan.return_value = [
            {'_source': {'foo': 1}},
            {'_source': {'foo': 2}},
            {'_source': {'foo': 3}},
            {'_source': {'foo': 4}}
        ]
        mock_elastic.return_value = mock.MagicMock()

        # no implicit sink since we just want to test the elastic read call
        read('elastic', batch=2).execute(implicit_sink=None)

        # 2 batches + eof
        expect(mock_push.call_args_list).to.have.length(3)

        # 1st batch
        points = [point.json() for point in mock_push.call_args_list[0][0][0]]
        expect(points).to.eq([
            {'foo': 1},
            {'foo': 2}
        ])

        # 2nd batch
        points = [point.json() for point in mock_push.call_args_list[1][0][0]]
        expect(points).to.eq([
            {'foo': 3},
            {'foo': 4}
        ])

        expect(mock_scan.call_args).to.eq(
            mock.call(mock_elastic.return_value,
                      index='_all',
                      preserve_order=True,
                      query={
                          'sort': ['time'],
                          'query': {
                              'match_all': {}
                          }
                      }))

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.bulk')
    def test_write_can_handle_custom_host_and_port(self, mock_bulk, mock_elastic):
        mock_elastic.return_value = {}
        mock_bulk.return_value = (None, [])
        (
            emit(limit=1, start='2016-01-01')
            | write('elastic', host='bananas', port=9999)
        ).execute()
        expect(mock_elastic.call_args).to.eq(mock.call('bananas', 9999))

    @mock.patch('flume.logger.error')
    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.bulk')
    def test_write_handles_errors(self, mock_bulk, mock_elastic, mock_error):
        mock_elastic.return_value = {}
        mock_bulk.return_value = (None, ['oops'])

        with self.assertRaisesRegexp(FlumeException,
                                     'errors while writing to elasticsearch'):
            (
                emit(limit=1, start='2016-01-01')
                | write('elastic', host='bananas', port=9999)
            ).execute()

        expect(mock_error.call_args).to.eq(mock.call('oops'))

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.bulk')
    def test_write_uses_specified_batch_size(self, mock_bulk, mock_elastic):
        mock_elastic.return_value = {}
        mock_bulk.return_value = (None, [])

        (
            emit(limit=3, start='2016-01-01')
            | write('elastic', host='bananas', port=9999, batch=2)
        ).execute()

        expect(mock_bulk.call_args_list).to.eq([
            mock.call({}, [
                {
                    'time': '2016-01-01T00:00:00.000Z',
                    '_type': 'metric',
                    '_index': 'metrics'
                },
                {
                    'time': '2016-01-01T00:00:01.000Z',
                    '_type': 'metric',
                    '_index': 'metrics'
                }
            ]),
            mock.call({}, [
                {
                    'time': '2016-01-01T00:00:02.000Z',
                    '_type': 'metric',
                    '_index': 'metrics'
                }
            ])
        ])

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.bulk')
    def test_write_timeless_points(self, mock_bulk, mock_elastic):
        mock_elastic.return_value = {}
        mock_bulk.return_value = (None, [])

        (
            emit(limit=3, start='2016-01-01')
            | put(count=count())
            | remove('time')
            | write('elastic', host='bananas', port=9999)
        ).execute()

        expect(mock_bulk.call_args_list).to.eq([
            mock.call({}, [
                {'count': 1, '_type': 'metric', '_index': 'metrics'},
                {'count': 2, '_type': 'metric', '_index': 'metrics'},
                {'count': 3, '_type': 'metric', '_index': 'metrics'}
            ])
        ])

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.bulk')
    def test_write_can_points_with_time(self, mock_bulk, mock_elastic):
        mock_elastic.return_value = {}
        mock_bulk.return_value = (None, [])

        (
            emit(limit=3, start='2016-01-01')
            | put(count=count())
            | write('elastic', host='bananas', port=9999, batch=3)
        ).execute()

        expect(mock_bulk.call_args_list).to.eq([
            mock.call({}, [
                {
                    '_type': 'metric',
                    '_index': 'metrics',
                    'time': '2016-01-01T00:00:00.000Z',
                    'count': 1
                },
                {
                    '_type': 'metric',
                    '_index': 'metrics',
                    'time': '2016-01-01T00:00:01.000Z',
                    'count': 2
                },
                {
                    '_type': 'metric',
                    '_index': 'metrics',
                    'time': '2016-01-01T00:00:02.000Z',
                    'count': 3
                }
            ])
        ])

    @mock.patch('elasticsearch.helpers.scan')
    def test_optimizes_head(self, mock_scan):
        mock_scan.return_value = [
            {'_source': {'foo': 'bar'}},
            {'_source': {'foo': 'bar'}},
            {'_source': {'foo': 'bar'}},
            {'_source': {'foo': 'bar'}},
            {'_source': {'foo': 'bar'}},
            {'_source': {'foo': 'bar'}},
            {'_source': {'foo': 'bar'}},
            {'_source': {'foo': 'bar'}},
            {'_source': {'foo': 'bar'}}
        ]
       
        results = []

        a = read('elastic', index='flume_data_with_time')
        b = head(5)
        c = memory(results)
        (a | b | c).execute()

        expect(results).to.have.length(5)
        expect(a.stats.points_pushed).to.eq(5)
        expect(a.stats.points_pulled).to.eq(0)

        expect(b.stats.points_pushed).to.eq(0)
        expect(b.stats.points_pulled).to.eq(0)

        expect(c.stats.points_pushed).to.eq(0)
        expect(c.stats.points_pulled).to.eq(5)

    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.Elasticsearch.search')
    def test_optimizes_count(self, mock_search, mock_elastic):
        elastic = mock.MagicMock(**{
            'search.return_value': {
                'aggregations': {
                    'count': {
                        'value': 10
                    }
                },
                'hits': {
                    'hits': [
                        {'_source': {'time': '2016-01-01T00:00:00.000Z'}}
                    ]
                }
            }
        })
        mock_elastic.return_value = elastic
        results = []

        a = read('elastic',
                 index='flume_data_with_time')
        b = reduce(count=count())
        c = memory(results)
        (a | b | c).execute()

        expect(results).to.eq([{
            'time': '2016-01-01T00:00:00.000Z',
            'count': 10
        }])
        expect(a.stats.points_pushed).to.eq(1)
        expect(a.stats.points_pulled).to.eq(0)

        expect(b.stats.points_pushed).to.eq(0)
        expect(b.stats.points_pulled).to.eq(0)

        expect(c.stats.points_pushed).to.eq(0)
        expect(c.stats.points_pulled).to.eq(1)

        expect(elastic.search.call_args).to.eq(
            mock.call(body={
                'aggs': {
                    'count': {
                        'value_count': {
                            'field': '_type'
                        }
                    }
                },
                'sort': ['time'],
                'size': 1
            },
            index='flume_data_with_time'))

    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.Elasticsearch.search')
    def test_optimizes_maximum(self, mock_search, mock_elastic):
        elastic = mock.MagicMock(**{
            'search.return_value': {
                'aggregations': {
                    'max': {
                        'value': 10
                    }
                },
                'hits': {
                    'hits': [
                        {'_source': {'time': '2016-01-01T00:00:00.000Z'}}
                    ]
                }
            }
        })
        mock_elastic.return_value = elastic
        results = []

        a = read('elastic',
                 index='flume_data_with_time')
        b = reduce(max=maximum('count'))
        c = memory(results)
        (a | b | c).execute()

        expect(results).to.eq([{
            'time': '2016-01-01T00:00:00.000Z',
            'max': 10
        }])
        expect(a.stats.points_pushed).to.eq(1)
        expect(a.stats.points_pulled).to.eq(0)

        expect(b.stats.points_pushed).to.eq(0)
        expect(b.stats.points_pulled).to.eq(0)

        expect(c.stats.points_pushed).to.eq(0)
        expect(c.stats.points_pulled).to.eq(1)

        expect(elastic.search.call_args).to.eq(
            mock.call(body={
                'aggs': {
                    'max': {
                        'max': {
                            'field': 'count'
                        }
                    }
                },
                'sort': ['time'],
                'size': 1
            },
            index='flume_data_with_time'))

    @mock.patch('elasticsearch.Elasticsearch')
    @mock.patch('elasticsearch.Elasticsearch.search')
    def test_optimizes_minimum(self, mock_search, mock_elastic):
        elastic = mock.MagicMock(**{
            'search.return_value': {
                'aggregations': {
                    'max': {
                        'value': 1
                    }
                },
                'hits': {
                    'hits': [
                        {'_source': {'time': '2016-01-01T00:00:00.000Z'}}
                    ]
                }
            }
        })
        mock_elastic.return_value = elastic
        results = []

        a = read('elastic',
                 index='flume_data_with_time')
        b = reduce(min=minimum('count'))
        c = memory(results)
        (a | b | c).execute()

        expect(results).to.eq([{
            'time': '2016-01-01T00:00:00.000Z',
            'max': 1
        }])
        expect(a.stats.points_pushed).to.eq(1)
        expect(a.stats.points_pulled).to.eq(0)

        expect(b.stats.points_pushed).to.eq(0)
        expect(b.stats.points_pulled).to.eq(0)

        expect(c.stats.points_pushed).to.eq(0)
        expect(c.stats.points_pulled).to.eq(1)

        expect(elastic.search.call_args).to.eq(
            mock.call(body={
                'aggs': {
                    'min': {
                        'min': {
                            'field': 'count'
                        }
                    }
                },
                'sort': ['time'],
                'size': 1
            },
            index='flume_data_with_time'))
