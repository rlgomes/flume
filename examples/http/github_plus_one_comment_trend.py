"""
Example using http adapter to read github issue comments and be able to see
what the trend of +1'ing has been on a specific issue over time.

Few things to note:

    1. been watching this specific issue on kibana for ages and that is why I
       have also been watching the trend to see when this actually issue gets
       attention.
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
         url='https://api.github.com/repos/%s/%s/issues/%s/comments' % (owner, repo, issue),
         time='created_at',
         cache='http_cache')
    | filter('"+1" in body')
    | reduce(value=count(), every='1 month')
    | put(name='+1 on issue', 
          date=date.strftime('time', '%Y-%m'))
    | barchart('gnuplot', category='date')
).execute()
