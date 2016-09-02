"""
elastic adapter query conversion unittests
"""
import time
import unittest

import requests

from elasticsearch import Elasticsearch
from robber import expect

from flume import *


class ElasticTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        es = Elasticsearch()

        for index in ['flume_data_with_time',
                      'flume_data_with_created_at',
                      'flume_data_timeless']:
            if es.indices.exists(index):
                es.indices.delete(index)

        # create 10 points in a test index
        (
            emit(limit=10, start='2016-01-01')
            | put(string=iterate(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']))
            | put(integer=count())
            | put(float=math.ceil('integer'))
            | write('elastic', index='flume_data_with_time')
        ).execute()

        # elasticsearch commit delay
        time.sleep(1)

    def test_elastic_read_fails_on_inexistent_index(self):
        try:
            (
                read('elastic',
                     index='bananas',
                     filter='foo=="bananas"')
            ).execute()
        except Exception as exception:
            expect(str(exception)).to.contain('no such index')

    def test_elastic_read_empty(self):
        results = []

        (
            read('elastic',
                 index='flume_data_with_time',
                 filter='foo=="bananas"')
            | memory(results)
        ).execute()

        expect(results).to.eq([])

    def test_elastic_read_with_small_batch(self):
        results = []

        (
            read('elastic',
                 index='flume_data_with_time',
                 filter='integer > 0',
                 batch=2)
            | memory(results)
        ).execute()
        expect(results).to.have.length(10)

    def test_elastic_read_with_filter_eq_string(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='string == "h"')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0}
        ])

    def test_elastic_read_with_filter_eq_integer(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='integer == 8')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0}
        ])

    def test_elastic_read_with_filter_eq_float(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='float == 8.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0}
        ])

    def test_elastic_read_with_filter_neq_string(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='string != "h"')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0},
            {'time': '2016-01-01T00:00:03.000Z', 'string': 'd', 'integer': 4, 'float': 4.0},
            {'time': '2016-01-01T00:00:04.000Z', 'string': 'e', 'integer': 5, 'float': 5.0},
            {'time': '2016-01-01T00:00:05.000Z', 'string': 'f', 'integer': 6, 'float': 6.0},
            {'time': '2016-01-01T00:00:06.000Z', 'string': 'g', 'integer': 7, 'float': 7.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_neq_integer(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='integer != 8')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0},
            {'time': '2016-01-01T00:00:03.000Z', 'string': 'd', 'integer': 4, 'float': 4.0},
            {'time': '2016-01-01T00:00:04.000Z', 'string': 'e', 'integer': 5, 'float': 5.0},
            {'time': '2016-01-01T00:00:05.000Z', 'string': 'f', 'integer': 6, 'float': 6.0},
            {'time': '2016-01-01T00:00:06.000Z', 'string': 'g', 'integer': 7, 'float': 7.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_neq_float(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='float != 8.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0},
            {'time': '2016-01-01T00:00:03.000Z', 'string': 'd', 'integer': 4, 'float': 4.0},
            {'time': '2016-01-01T00:00:04.000Z', 'string': 'e', 'integer': 5, 'float': 5.0},
            {'time': '2016-01-01T00:00:05.000Z', 'string': 'f', 'integer': 6, 'float': 6.0},
            {'time': '2016-01-01T00:00:06.000Z', 'string': 'g', 'integer': 7, 'float': 7.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_gt_string(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='string > "g"')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_gt_integer(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='integer > 7')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_gt_float(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='float > 7.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_gte_string(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='string >= "h"')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_gte_integer(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='integer >= 8')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_gte_float(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='float >= 8.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_elastic_read_with_filter_lt_string(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='string < "d"')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0}
        ])

    def test_elastic_read_with_filter_lt_integer(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='integer < 4')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0}
        ])

    def test_elastic_read_with_filter_lt_float(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='float < 4.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0}
        ])

    def test_elastic_read_with_filter_lte_string(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='string <= "c"')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0}
        ])

    def test_elastic_read_with_filter_lte_integer(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='integer <= 3')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0}
        ])

    def test_elastic_read_with_filter_lte_float(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='float <= 3.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0}
        ])

    def test_elastic_read_with_and_filter(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='string == "a" and float == 1.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0}
        ])

    def test_elastic_read_with_or_filter(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='string == "a" or float == 3.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0}
        ])

    def test_elastic_read_with_not_filter(self):
        results = []
        (
            read('elastic', index='flume_data_with_time', filter='not(string == "h")')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:01.000Z', 'string': 'b', 'integer': 2, 'float': 2.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0},
            {'time': '2016-01-01T00:00:03.000Z', 'string': 'd', 'integer': 4, 'float': 4.0},
            {'time': '2016-01-01T00:00:04.000Z', 'string': 'e', 'integer': 5, 'float': 5.0},
            {'time': '2016-01-01T00:00:05.000Z', 'string': 'f', 'integer': 6, 'float': 6.0},
            {'time': '2016-01-01T00:00:06.000Z', 'string': 'g', 'integer': 7, 'float': 7.0},
            {'time': '2016-01-01T00:00:08.000Z', 'string': 'i', 'integer': 9, 'float': 9.0},
            {'time': '2016-01-01T00:00:09.000Z', 'string': 'j', 'integer': 10, 'float': 10.0}
        ])

    def test_can_write_and_read_timeless_points(self):
        (
            emit(limit=3, start='2016-01-01')
            | put(foo='bar',count=count())
            | keep('foo', 'count')
            | write('elastic', index='flume_data_timeless')
        ).execute()

        # elasticsearch commit delay
        time.sleep(1)

        results = []
        (
            read('elastic', index='flume_data_timeless', time=None)
            | memory(results)
        ).execute()

        expect(results).to.have.length(3)
        expect(results).to.contain({'foo': 'bar', 'count': 1})
        expect(results).to.contain({'foo': 'bar', 'count': 2})
        expect(results).to.contain({'foo': 'bar', 'count': 3})

    def test_can_write_and_read_points_with_different_time_field(self):
        (
            emit(limit=3, start='2016-01-01')
            | put(foo='bar', count=count(), created_at='{time}')
            | keep('foo', 'count', 'created_at')
            | write('elastic', index='flume_data_with_created_at')
        ).execute()

        # elasticsearch commit delay
        time.sleep(1)

        results = []
        (
            read('elastic', index='flume_data_with_created_at', time='created_at')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'foo': 'bar', 'count': 1},
            {'time': '2016-01-01T00:00:01.000Z', 'foo': 'bar', 'count': 2},
            {'time': '2016-01-01T00:00:02.000Z', 'foo': 'bar', 'count': 3}
        ])

    def test_optimizes_head(self):
        results = []

        a = read('elastic',
                 index='flume_data_with_time')
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
