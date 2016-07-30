"""
elastic adapter query conversion unittests
"""
import time
import unittest

import requests

from docker import Client
from robber import expect

from flume import *


class ElasticTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cli = Client()
        host_config = cls.cli.create_host_config(port_bindings={
            9200:9200
        })
        cls.container = cls.cli.create_container(image='elasticsearch:2.3.3',
                                                 ports=[9200],
                                                 host_config=host_config)
        cls.cli.start(container=cls.container.get('Id'))

        # wait for elasticsearch to be running
        response = None
        start = time.time()
        while (response is None or response.status_code != 200) and \
              (time.time() - start) < 30000: # timeout after 30s
            try:
                response = requests.get('http://localhost:9200/_cluster/health')
            except requests.ConnectionError:
                pass
            time.sleep(1)

        if response is None or response.status_code != 200:
            raise Exception('unable to bring up elasticsearch v2.3.3')

        # create 10 points in a test index
        (
            emit(limit=10, start='2016-01-01')
            | put(string=iterate(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']),
                  integer=count(),
                  float=math.ceil('integer'))
            | write('elastic', index='test_data')
        ).execute()

        # elasticsearch commit delay
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.cli.stop(container=cls.container.get('Id'))
        cls.cli.wait(container=cls.container.get('Id'))

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
                 index='test_data',
                 filter='foo=="bananas"')
            | memory(results)
        ).execute()

        expect(results).to.eq([])

    def test_elastic_read_with_small_batch(self):
        results = []

        (
            read('elastic',
                 index='test_data',
                 filter='integer > 0',
                 batch=2)
            | memory(results)
        ).execute()
        expect(results).to.have.length(10)

    def test_elastic_read_with_filter_eq_string(self):
        results = []
        (
            read('elastic', index='test_data', filter='string == "h"')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0}
        ])

    def test_elastic_read_with_filter_eq_integer(self):
        results = []
        (
            read('elastic', index='test_data', filter='integer == 8')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0}
        ])

    def test_elastic_read_with_filter_eq_float(self):
        results = []
        (
            read('elastic', index='test_data', filter='float == 8.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:07.000Z', 'string': 'h', 'integer': 8, 'float': 8.0}
        ])

    def test_elastic_read_with_filter_neq_string(self):
        results = []
        (
            read('elastic', index='test_data', filter='string != "h"')
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
            read('elastic', index='test_data', filter='integer != 8')
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
            read('elastic', index='test_data', filter='float != 8.0')
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
            read('elastic', index='test_data', filter='string > "g"')
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
            read('elastic', index='test_data', filter='integer > 7')
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
            read('elastic', index='test_data', filter='float > 7.0')
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
            read('elastic', index='test_data', filter='string >= "h"')
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
            read('elastic', index='test_data', filter='integer >= 8')
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
            read('elastic', index='test_data', filter='float >= 8.0')
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
            read('elastic', index='test_data', filter='string < "d"')
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
            read('elastic', index='test_data', filter='integer < 4')
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
            read('elastic', index='test_data', filter='float < 4.0')
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
            read('elastic', index='test_data', filter='string <= "c"')
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
            read('elastic', index='test_data', filter='integer <= 3')
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
            read('elastic', index='test_data', filter='float <= 3.0')
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
            read('elastic', index='test_data', filter='string == "a" and float == 1.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0}
        ])

    def test_elastic_read_with_or_filter(self):
        results = []
        (
            read('elastic', index='test_data', filter='string == "a" or float == 3.0')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'time': '2016-01-01T00:00:00.000Z', 'string': 'a', 'integer': 1, 'float': 1.0},
            {'time': '2016-01-01T00:00:02.000Z', 'string': 'c', 'integer': 3, 'float': 3.0}
        ])

    def test_elastic_read_with_not_filter(self):
        results = []
        (
            read('elastic', index='test_data', filter='not(string == "h")')
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
