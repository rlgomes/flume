"""
elastic adapter query conversion unittests
"""
import unittest

from robber import expect
from flume.adapters.elastic.query import filter_to_es_query
from flume.exceptions import FlumeException


class ElasticQueryTest(unittest.TestCase):

    def test_default_filter_is_match_all(self):
        expect(filter_to_es_query(None)).to.eq({
            'match_all': {}
        })

    def test_invalid_assignment_query(self):
        try:
            expect(filter_to_es_query('foo="bar"'))
            raise Exception('previous statement should have failed')
        except FlumeException as exception:
            expect(exception.message).to.contain('invalid filter expression: foo="bar"')

    def test_single_string_eq_query(self):
        expect(filter_to_es_query('foo=="bar"')).to.eq({
            'constant_score': {
                'filter': {
                    'term': {'foo': 'bar'}
                }
            }
        })

    def test_single_string_neq_query(self):
        expect(filter_to_es_query('foo!="bar"')).to.eq({
            'constant_score': {
                'filter': {
                    'not': {
                        'term': {'foo': 'bar'}
                    }
                }
            }
        })

    def test_single_term_integer_query(self):
        expect(filter_to_es_query('foo==2')).to.eq({
            'constant_score': {
                'filter': {
                    'term': {'foo': 2}
                }
            }
        })

    def test_single_and_query(self):
        expect(filter_to_es_query('foo==1 and fizz=="buzz"')).to.eq({
            'constant_score': {
                'filter': {
                    'bool': {
                        'must': [
                            {'term': {'foo': 1}},
                            {'term': {'fizz': 'buzz'}}
                        ]
                    }
                }
            }
        })

    def test_single_or_query(self):
        expect(filter_to_es_query('foo==1 or fizz=="buzz"')).to.eq({
            'constant_score': {
                'filter': {
                    'bool': {
                        'minimum_should_match': 1,
                        'should': [
                            {'term': {'foo': 1}},
                            {'term': {'fizz': 'buzz'}}
                        ]
                    }
                }
            }
        })

    def test_and_with_nested_or_query(self):
        query = 'foo==1 and (fizz=="buzz" or fizz=="bar")'

        expect(filter_to_es_query(query)).to.eq({
            'constant_score': {
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'term': {'foo': 1}
                            },
                            {
                                'bool': {
                                    'minimum_should_match': 1,
                                    'should': [
                                        {'term': {'fizz': 'buzz'}},
                                        {'term': {'fizz': 'bar'}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        })

    def test_or_with_nested_and_query(self):
        query = 'foo==1 or (fizz=="buzz" and fizz=="bar")'
        expect(filter_to_es_query(query)).to.eq({
            'constant_score': {
                'filter': {
                    'bool': {
                        'minimum_should_match': 1,
                        'should': [
                            {
                                'term': {'foo': 1}
                            },
                            {
                                'bool': {
                                    'must': [
                                        {'term': {'fizz': 'buzz'}},
                                        {'term': {'fizz': 'bar'}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        })

    def test_single_integer_lt_query(self):
        expect(filter_to_es_query('foo < 3')).to.eq({
            'constant_score': {
                'filter': {
                    'range': {
                        'foo':  {
                            'lt': 3
                        }
                    }
                }
            }
        })

    def test_single_integer_lte_query(self):
        expect(filter_to_es_query('foo <= 3')).to.eq({
            'constant_score': {
                'filter': {
                    'range': {
                        'foo':  {
                            'lte': 3
                        }
                    }
                }
            }
        })

    def test_single_integer_gt_query(self):
        expect(filter_to_es_query('foo > 3')).to.eq({
            'constant_score': {
                'filter': {
                    'range': {
                        'foo':  {
                            'gt': 3
                        }
                    }
                }
            }
        })

    def test_single_integer_gte_query(self):
        expect(filter_to_es_query('foo >= 3')).to.eq({
            'constant_score': {
                'filter': {
                    'range': {
                        'foo':  {
                            'gte': 3
                        }
                    }
                }
            }
        })

    def test_not_operator_on_eq_query(self):
        expect(filter_to_es_query('not(foo=="bar")')).to.eq({
            'constant_score': {
                'filter': {
                    'bool': {
                        'must_not': {
                            'term': {'foo': 'bar'}
                        }
                    }
                }
            }
        })

