"""
elastic adapter query conversion unittests
"""
import unittest
import mock

from robber import expect
from elasticsearch.exceptions import RequestError
from flume.exceptions import FlumineException

from flume import *


class ElasticTest(unittest.TestCase):

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_handle_custom_host_and_port(self, mock_scan, mock_elastic):
        mock_elastic.return_value = {}
        read('elastic', host='bananas', port=9999).execute()
        expect(mock_elastic.call_args).to.eq(mock.call('bananas', 9999))

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_reports_nicer_exception_on_mapping_issue(self, mock_scan, mock_elastic):
        mock_elastic.return_value = {}
        mock_scan.side_effect = RequestError(400, 'oh doh', {
            'error': {
                'type': 'search_phase_execution_exception',
                'root_cause': [
                    {
                        'reason': 'No mapping found for [time] in order to sort on'
                    }
                ]
            }
        })

        with self.assertRaisesRegexp(FlumineException,
                                     'Time field "time" not found in data, ' + 
                                     'set time to the appropriate value or ' +
                                     'None to query timeless data'):
            read('elastic').execute()

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_reports_exceptions_on_non_mapping_issue(self, mock_scan, mock_elastic):
        mock_elastic.return_value = {}
        mock_scan.side_effect = RequestError(400, 'oh doh', {
            'error': {
                'type': 'some_other_phase_execution_exception'
            }
        })

        with self.assertRaisesRegexp(RequestError, 'oh doh'):
            read('elastic').execute()

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_handle_empty_response(self, mock_scan, mock_elastic):
        mock_scan.return_value = []
        mock_elastic.return_value = {}
        results = []

        (read('elastic') | memory(results)).execute()

        expect(results).to.eq([])
        expect(mock_scan.call_args).to.eq(mock.call({},
                                                    index='_all',
                                                    query={
                                                        'sort': ['time'],
                                                        'query': {
                                                            'match_all': {}
                                                        }
                                                    },
                                                    preserve_order=True))

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_handle_a_single_timeless_point(self, mock_scan, mock_elastic):
        mock_scan.return_value = [{'_source': {'foo': 'bar'}}]
        mock_elastic.return_value = {}
        results = []

        (read('elastic', time=None) | memory(results)).execute()

        expect(results).to.eq([{'foo': 'bar'}])
        expect(mock_scan.call_args).to.eq(mock.call({},
                                                    index='_all',
                                                    query={
                                                        'query': {
                                                            'match_all': {}
                                                        }
                                                    },
                                                    preserve_order=True))

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_handle_a_single_point_with_time(self, mock_scan, mock_elastic):
        mock_scan.return_value = [{'_source': {'foo': 'bar'}}]
        mock_elastic.return_value = {}
        results = []

        (read('elastic') | memory(results)).execute()

        expect(results).to.eq([{'foo': 'bar'}])
        expect(mock_scan.call_args).to.eq(mock.call({},
                                                    index='_all',
                                                    query={
                                                        'sort': ['time'],
                                                        'query': {
                                                            'match_all': {}
                                                        }
                                                    },
                                                    preserve_order=True))

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_read_from_a_specific_index(self, mock_scan, mock_elastic):
        mock_scan.return_value = [{'_source': {'foo': 'bar'}}]
        mock_elastic.return_value = {}
        results = []
        (read('elastic', index='foo') | memory(results)).execute()

        expect(results).to.eq([{'foo': 'bar'}])
        expect(mock_scan.call_args).to.eq(mock.call({},
                                                    index='foo',
                                                    query={
                                                        'sort': ['time'],
                                                        'query': {
                                                            'match_all': {}
                                                        }
                                                    },
                                                    preserve_order=True))

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_read_from_a_specific_index(self, mock_scan, mock_elastic):
        mock_scan.return_value = [{'_source': {'foo': 'bar'}}]
        mock_elastic.return_value = {}
        results = []
        (read('elastic', index='foo') | memory(results)).execute()

        expect(results).to.eq([{'foo': 'bar'}])
        expect(mock_scan.call_args).to.eq(mock.call({},
                                                    index='foo',
                                                    query={
                                                        'sort': ['time'],
                                                        'query': {
                                                            'match_all': {}
                                                        }
                                                    },
                                                    preserve_order=True))

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_can_read_with_filter(self, mock_scan, mock_elastic):
        mock_scan.return_value = [{'_source': {'foo': 'bar'}}]
        mock_elastic.return_value = {}
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

        expect(mock_scan.call_args).to.eq(mock.call({},
                                                    index='foo',
                                                    query=query,
                                                    preserve_order=True))

    @mock.patch('flume.sources.read.push')
    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.scan')
    def test_read_abides_by_batch_size(self, mock_scan, mock_elastic, mock_push):
        mock_scan.return_value = [
            {'_source': {'foo': 1}},
            {'_source': {'foo': 2}},
            {'_source': {'foo': 3}},
            {'_source': {'foo': 4}}
        ]

        mock_elastic.return_value = {}
        (
            read('elastic', batch=2)
        ).execute()

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

        expect(mock_scan.call_args).to.eq(mock.call({},
                                                    index='_all',
                                                    query={
                                                        'sort': ['time'],
                                                        'query': {
                                                            'match_all': {}
                                                        }
                                                    },
                                                    preserve_order=True))

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

        with self.assertRaisesRegexp(FlumineException,
                                     'errors while writing to elasticsearch'):
            (
                emit(limit=1, start='2016-01-01')
                | write('elastic', host='bananas', port=9999)
            ).execute()

        expect(mock_error.call_args).to.eq(mock.call('oops'))

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
            mock.call({}, [{'count': 1, '_type': 'metric', '_index': '_all'}]),
            mock.call({}, [{'count': 2, '_type': 'metric', '_index': '_all'}]),
            mock.call({}, [{'count': 3, '_type': 'metric', '_index': '_all'}])
        ])

    @mock.patch('flume.adapters.elastic._get_elasticsearch')
    @mock.patch('elasticsearch.helpers.bulk')
    def test_write_can_points_with_time(self, mock_bulk, mock_elastic):
        mock_elastic.return_value = {}
        mock_bulk.return_value = (None, [])

        (
            emit(limit=3, start='2016-01-01')
            | put(count=count())
            | write('elastic', host='bananas', port=9999)
        ).execute()

        expect(mock_bulk.call_args_list).to.eq([
            mock.call({}, [{
                '_type': 'metric',
                '_index': '_all',
                'time': '2016-01-01T00:00:00.000Z',
                'count': 1
            }]),
            mock.call({}, [{
                '_type': 'metric',
                '_index': '_all',
                'time': '2016-01-01T00:00:01.000Z',
                'count': 2
            }]),
            mock.call({}, [{
                '_type': 'metric',
                '_index': '_all',
                'time': '2016-01-01T00:00:02.000Z',
                'count': 3
            }])
        ])
