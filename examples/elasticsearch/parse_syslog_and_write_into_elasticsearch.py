"""
flume program that reads the syslog file at examples/grok/syslog and
parses the lines as JSON which it then ingests into a locally running
instance of elasticsearch. If you don't have a locally running elasticsearch
instance then you can use docker (https://www.docker.com/) to spin one up
locally like so:

docker run -p 9200:9200 elasticsearch:2.3.3

after running this script you can very easily verify the logs are there
by hitting the following elasticsearch query:

http://localhost:9200/_search

which will return a JSON containing 274 hits in the response from elasticsearch.
"""
from flume import *

(
    read('stdio',
         format='grok',
         pattern='%{SYSLOGLINE}',
         file='examples/grok/syslog',
         time='timestamp')
    | write('elastic',
            index='syslog',
            host='localhost',
            port=9200)
).execute()
