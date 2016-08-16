import unittest

import mock

from dici import dici
from flume import *
from flume.exceptions import FlumineException
from robber import expect

class GithubIssuesTest(unittest.TestCase):
    """
    verify that the third-party utilities for github issues works
    """

    @mock.patch('requests.request')
    def test_can_handle_a_failure_from_user_issues(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'oh shoot',
            'headers': [],
            'json': lambda: []
        })

        with self.assertRaisesRegexp(FlumineException, '400: oh shoot'):
            github.issues.user('FAKETOKEN').execute()

    @mock.patch('requests.request')
    def test_can_read_user_issues(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.issues.user(oauth='FAKETOKEN')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/user/issues',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_read_user_issues_with_parameters(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.issues.user(oauth='FAKETOKEN', filter='mentioned')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/user/issues?filter=mentioned',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_handle_a_failure_from_orgs_issues(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'oh shoot',
            'headers': [],
            'json': lambda: []
        })

        with self.assertRaisesRegexp(FlumineException, '400: oh shoot'):
            github.issues.orgs('whocares', 'FAKETOKEN').execute()

    @mock.patch('requests.request')
    def test_can_read_orgs_issues(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (github.issues.orgs('whocares', 'FAKETOKEN') | memory(results)).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/orgs/whocares/issues',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_read_orgs_issues_with_parameters(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.issues.orgs('whocares',
                               oauth='FAKETOKEN',
                               state='open')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/orgs/whocares/issues?state=open',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_handle_a_failure_from_repo_issues(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'oh shoot',
            'headers': [],
            'json': lambda: []
        })

        with self.assertRaisesRegexp(FlumineException, '400: oh shoot'):
            github.issues.repo('whocares',
                               'somerepo',
                               oauth='FAKETOKEN').execute()

    @mock.patch('requests.request')
    def test_can_read_repo_issues(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (github.issues.repo('whocares',
                            'somerepo',
                            oauth='FAKETOKEN') | memory(results)).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/repos/whocares/somerepo/issues',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_read_repo_issues_with_parameters(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.issues.repo('whocares',
                            'somerepo',
                            oauth='FAKETOKEN',
                            sort='updated')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/repos/whocares/somerepo/issues?sort=updated',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_handle_a_failure_from_issue(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'oh shoot',
            'headers': [],
            'json': lambda: []
        })

        with self.assertRaisesRegexp(FlumineException, '400: oh shoot'):
            github.issues.issue('whocares',
                                'somerepo',
                                1,
                                oauth='FAKETOKEN').execute()

    @mock.patch('requests.request')
    def test_can_read_issue(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.issues.issue('whocares', 'otherrepo', 1, oauth='FAKETOKEN')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/repos/whocares/otherrepo/issues/1',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_handle_a_failure_from_issue_comments(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 400,
            'text': 'oh shoot',
            'headers': [],
            'json': lambda: []
        })

        with self.assertRaisesRegexp(FlumineException, '400: oh shoot'):
            github.issues.comments('whocares',
                                   'somerepo',
                                   1,
                                   oauth='FAKETOKEN').execute()

    @mock.patch('requests.request')
    def test_can_read_issue_comments(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.issues.comments('whocares', 'otherrepo', 1, oauth='FAKETOKEN')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/repos/whocares/otherrepo/issues/1/comments',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])

    @mock.patch('requests.request')
    def test_can_read_issue_comments_with_parameters(self, mock_request):
        mock_request.return_value = dici(**{
            'status_code': 200,
            'headers': [],
            'json': lambda: [{'created_at': '2016-01-01T00:00:00.000Z'}]
        })

        results = []
        (
            github.issues.comments('whocares',
                                   'otherrepo',
                                   1,
                                   oauth='FAKETOKEN',
                                   since='2016-01-01')
            | memory(results)
        ).execute()

        expect(results).to.eq([{'time': '2016-01-01T00:00:00.000Z'}])
        expect(mock_request.call_args_list).to.eq([
            mock.call('GET',
                      'https://api.github.com/repos/whocares/otherrepo/issues/1/comments?since=2016-01-01',
                      headers={
                          'Authorization': 'token FAKETOKEN'
                      })
        ])
