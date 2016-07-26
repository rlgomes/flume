"""
this program depends on having already executed the 
parse_syslog_and_write_into_elasticsearch.py before so that the syslog data
is now residing in the locally running elasticsearch instance.
"""
from flume import *

(
    read('elastic',
         index='syslog',
         host='localhost',
         port=9200)
    | reduce(count=count(), by=['program'])
    | sort('count', order='desc')
    | head(5)
    | write('stdio')
).execute()
