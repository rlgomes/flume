"""
syslog flume extras that make reading from syslog files easy
"""
import os

from flume.procs import seq
from flume.sources import read

def __get_syslog_filenames(path):
    """
    internal utility to fetch the syslog files from the path provided knowing
    that the file starts with the prefix `syslog`
    """
    log_files = os.listdir(path)
    syslog_files = []
    for filename in log_files:
        if filename.startswith('syslog'):
            syslog_files.append(os.path.join(path, filename))

    return sorted(syslog_files, key=os.path.getmtime)


def syslog(logfile=None, path='/var/log/'):
    """
    syslog sink
    """
    if logfile is None:
        pipelines = []

        for logfile in __get_syslog_filenames(path):
            if logfile.endswith('.gz'):
                compression = 'gzip'

            else:
                compression = None

            pipelines.append(read('stdio',
                                  file=logfile,
                                  format='grok',
                                  pattern='%{SYSLOGLINE}',
                                  time='timestamp',
                                  compression=compression))

        return seq(*pipelines)
    else:
        if logfile.endswith('.gz'):
            compression = 'gzip'

        else:
            compression = None

        return read('stdio',
                    file=logfile,
                    format='grok',
                    pattern='%{SYSLOGLINE}',
                    time='timestamp',
                    compression=compression)
