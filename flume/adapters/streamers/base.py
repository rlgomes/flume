"""
streamer base class

"""
from flume.exceptions import FlumineException

class Streamer(object):

    def eof(self, stream):
        pass

    def read(self, stream):
        """
        read should return all of the data points present in the stream
        until the stream is empty
        """
        raise FlumineException('you must implement the read method')

    def write(self, stream, points):
        """
        write should write each of the points provided to the stream in
        the format of the output stream
        """
        raise FlumineException('you must implement the write method')
