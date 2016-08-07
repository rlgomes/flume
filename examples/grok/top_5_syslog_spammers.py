"""
flume program that calculates the top 5 programs that log to the syslog file
provided and writes them out to jsonlines format to the console
"""
from flume import *  

(
    read('stdio', format='grok', pattern='%{SYSLOGLINE}', file='examples/grok/syslog', time='timestamp')
    | reduce(count=count(), by=['program'])
    | sort('count', order='desc')
    | head(5)
    | write('stdio')
).execute()
