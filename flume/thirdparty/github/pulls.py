"""
github pulls API v3

  https://developer.github.com/v3/pulls

Not everything has been covered here as this is more of an example of how to
create a third party integration that makes getting external data into flume
easy.
"""

from flume.sources import read
from flume.thirdparty.github.util import github_url


def repo(owner,
         repo_name,
         oauth=None,
         **kwargs):
    headers = {}

    if oauth is not None:
        headers['Authorization'] = 'token %s' % oauth

    return read('http',
                url=github_url('repos/%s/%s/pulls' % (owner, repo_name),
                               **kwargs),
                time='created_at',
                headers=headers)

def commits(owner,
            repo_name,
            pull_number,
            oauth=None):
    headers = {}

    if oauth is not None:
        headers['Authorization'] = 'token %s' % oauth

    return read('http',
                url=github_url('repos/%s/%s/pulls/%s/commits' %
                               (owner, repo_name, pull_number)),
                time='created_at',
                headers=headers)
