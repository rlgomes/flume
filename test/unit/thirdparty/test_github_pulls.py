import unittest

import mock

from dici import dici
from flume import *
from flume.exceptions import FlumineException
from robber import expect

class GithubPullsTest(unittest.TestCase):
    """
    verify that the third-party utilities for github pulls works
    """

    @mock.patch('requests.request')
    def test_can_handle_a_failure_from_repo_pulls(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'oh shoot',
            'headers': [],
            'json': lambda: []
        })

        with self.assertRaisesRegexp(FlumineException, '400: oh shoot'):
            github.pulls.repo('whocares', 'repo', oauth='FAKETOKEN').execute()

    @mock.patch('requests.request')
    def test_can_read_repo_pulls(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.pulls.repo('whocares', 'repo', oauth='FAKETOKEN')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/repos/whocares/repo/pulls',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_read_repo_pulls_with_parameters(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.pulls.repo('whocares',
                              'repo',
                              oauth='FAKETOKEN',
                              state='closed')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/repos/whocares/repo/pulls?state=closed',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_handle_a_failure_from_pull_commits(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'oh shoot',
            'headers': [],
            'json': lambda: []
        })

        with self.assertRaisesRegexp(FlumineException, '400: oh shoot'):
            github.pulls.commits('whocares', 'repo', 1, oauth='FAKETOKEN').execute()

    @mock.patch('requests.request')
    def test_can_read_pulls_commits(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.pulls.commits('whocares', 'repo', 1, oauth='FAKETOKEN')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/repos/whocares/repo/pulls/1/commits',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])
