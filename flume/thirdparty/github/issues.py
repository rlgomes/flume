"""
github issues API v3

  https://developer.github.com/v3/issues/

Not everything has been covered here as this is more of an example of how to
create a third party integration that makes getting external data into flume
easy.
"""

from flume.sources import read
from flume.thirdparty.github.util import github_url


def user(oauth=None,
         **kwargs):
    headers = {
        'Authorization': 'token %s' % oauth
    }

    return read('http',
                url=github_url('user/issues', **kwargs),
                time='created_at',
                headers=headers)

def orgs(org_name,
         oauth=None,
         **kwargs):
    headers = {
        'Authorization': 'token %s' % oauth
    }

    return read('http',
                url=github_url('orgs/%s/issues' % org_name, **kwargs),
                time='created_at',
                headers=headers)

def repo(owner,
         repo_name,
         oauth=None,
         **kwargs):
    headers = {}

    if oauth is not None:
        headers['Authorization'] = 'token %s' % oauth

    return read('http',
                url=github_url('repos/%s/%s/issues' %
                                (owner, repo_name),
                                **kwargs),
                time='created_at',
                headers=headers)

def issue(owner,
          repo_name,
          issue_number,
          oauth=None,
          **kwargs):
    headers = {}

    if oauth is not None:
        headers['Authorization'] = 'token %s' % oauth

    return read('http',
                url=github_url('repos/%s/%s/issues/%s' %
                                (owner, repo_name, issue_number),
                                **kwargs),
                time='created_at',
                headers=headers)

def comments(owner,
             repo_name,
             issue_number,
             oauth=None,
             **kwargs):
    headers = {}

    if oauth is not None:
        headers['Authorization'] = 'token %s' % oauth

    return read('http',
                url=github_url('repos/%s/%s/issues/%s/comments' %
                                (owner, repo_name, issue_number),
                                **kwargs),
                time='created_at',
                headers=headers)
