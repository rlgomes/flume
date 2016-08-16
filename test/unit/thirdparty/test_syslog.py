import unittest

from robber import expect
from flume import *
from flume.exceptions import FlumineException

from flume.core import register_sink, register_proc, register_source

class SyslogTest(unittest.TestCase):
    """
    verify that the third-party utilities for syslog work as expected
    """

    def test_syslog_fails_when_path_does_not_exist(self):
        with self.assertRaisesRegexp(OSError, 'No such file or directory: \'/no/mans/land/\''):
            syslog(path='/no/mans/land/').execute()

    def test_syslog_can_find_a_single_syslog_by_path(self):
        results = []

        (
            syslog(path='test/unit/thirdparty/')
            | reduce(count=count())
            | keep('count')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'count':  274}
        ])

    def test_syslog_read_syslog_file_directly(self):
        results = []

        (
            syslog(logfile='test/unit/thirdparty/syslog')
            | reduce(count=count())
            | keep('count')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'count':  274}
        ])

    def test_syslog_can_read_compressed_and_not_compressed_syslog_files(self):
        results = []

        (
            syslog(path='test/unit/thirdparty/logs/')
            | reduce(count=count())
            | keep('count')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'count':  1200}
        ])

    def test_syslog_can_handle_compressed_direct_logfile(self):
        results = []

        (
            syslog(logfile='test/unit/thirdparty/logs/syslog.1.gz')
            | reduce(count=count())
            | keep('count')
            | memory(results)
        ).execute()

        expect(results).to.eq([
            {'count':  926}
        ])
