"""
Example using http adapter to read github commits for a repo and calculate
the number of commits per author.login since the repo was first created.
Few things to note:

    1. Had to filter on `author != None` since sometimes there is no author
       section in the commit data (odd)

    2. Show casing how to do nested object references with `commit.author.date`
       and `author.login` references.

    3. Using the http caching feature so you if you rerun this against the same
       repository we don't have to redo each call and get blocked by github's
       rate limiting.
"""
from flume import *

try:
    # python 2 & 3 supporting magic
    input = raw_input
except NameError:
    pass

print('Github commit repo stats')
owner = raw_input('Name of the github repo owner (default: elastic): ') or 'elastic'
repo = raw_input('Name of the github repo (default: kibana): ') or 'kibana'
issue = raw_input('Isssue # (default: 1610): ') or '1610'

(
    read('http',
         url='https://api.github.com/repos/%s/%s/commits' % (owner, repo),
         time='commit.author.date',
         cache='http_cache')
    | filter('author != None')
    | reduce(value=count(), by=['author.login'])
    | put(name='commits per user')
    | sort('value')
    | barchart('gnuplot', category='author.login')
).execute()
