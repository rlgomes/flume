"""
stdio adapter
"""
import codecs
import re
import sys
import zlib

from flume.adapters.adapter import adapter
from flume.adapters import streamers
from flume.exceptions import FlumineException
from flume.point import Point
from flume import util

# For things to work in Python 3
# from: http://python-notes.curiousefficiency.org/en/latest/python3/text_file_processing.html#unicode-basics
# "Approach: use the 'latin-1' encoding to map byte values directly to the
#  first 256 Unicode code points. This is the closest equivalent Python 3
#  offers to the permissive Python 2 text handling model."
_DEFAULT_ENCODING = 'latin-1'


class InputStream(object):
    """
    input stream wrapper that gives us a few things:

      * override the behavior of readlines which doesn't actually stream data
        but attempts to read the whole input and break it into individual
        lines. We want the input to stream line by line and not block the
        pipeline.

      * with strip_ansi set to True this wrapper will make sure to strip any
        ANSI sequences from the stream.

      * handles compressed streams by decompressing using the algorithm
        specified by the compression option.
    """

    def __init__(self,
                 stream,
                 strip_ansi=False,
                 compression=None):
        self.stream = stream
        self.strip_ansi = strip_ansi
        self.decompressor = None
        self.__line_buffer = ''

        if compression is not None:
            if compression == 'gzip':
                self.decompressor = zlib.decompressobj(zlib.MAX_WBITS | 16)

            elif compression == 'zlib':
                self.decompressor = zlib.decompressobj(zlib.MAX_WBITS)

            elif compression == 'deflate':
                self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)

            else:
                raise FlumineException('unsupported compression [%s]' % compression)

    def __remove_ansi(self, line):
        return re.sub(r'\x1b[^A-Za-z]*[A-Za-z]', '', line)

    def read(self, size=1024):
        data = self.stream.read(size)

        if data is None:
            data = ''

        if self.decompressor is not None:
            if util.IS_PY2:
                data = self.decompressor.decompress(data)

            else:
                data = self.decompressor.decompress(data.encode(_DEFAULT_ENCODING))
                data = data.decode(_DEFAULT_ENCODING)

        if self.strip_ansi:
            data = self.__remove_ansi(data)

        return data

    def readline(self, limit=-1):
        index = self.__line_buffer.find('\n')

        while index == -1:
            data = self.read()

            if not data:
                data = self.__line_buffer
                self.__line_buffer = ''
                return data

            self.__line_buffer += data
            index = self.__line_buffer.find('\n')

        result = self.__line_buffer[:index]
        self.__line_buffer = self.__line_buffer[index + 1:]

        return result

    def readlines(self):

        while True:
            line = self.readline()

            if not line:
                break

            if self.strip_ansi:
                yield self.__remove_ansi(line)

            else:
                yield line

class OutputStream(object):

    def __init__(self,
                 stream,
                 compression=None):
        self.stream = stream
        self.compressor = None

        if compression is not None:
            if compression == 'gzip':
                self.compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                                   zlib.DEFLATED,
                                                   zlib.MAX_WBITS | 16)

            elif compression == 'zlib':
                self.compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                                   zlib.DEFLATED,
                                                   zlib.MAX_WBITS)

            elif compression == 'deflate':
                self.compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                                   zlib.DEFLATED,
                                                   -zlib.MAX_WBITS)

            else:
                raise FlumineException('unsupported compression [%s]' % compression)

    def write(self, data):
        if self.compressor is not None:
            if util.IS_PY2:
                data = self.compressor.compress(data)

            else:
                data = self.compressor.compress(data.encode(_DEFAULT_ENCODING))
                data = data.decode(_DEFAULT_ENCODING)

        self.stream.write(data)

    def flush(self):
        if self.compressor is not None:
            if util.IS_PY2:
                data = self.compressor.flush()
                self.stream.write(data)

            else:
                data = self.compressor.flush().decode(_DEFAULT_ENCODING)
                self.stream.write(data)

        self.stream.flush()

    def close(self):
        self.flush()
        self.stream.close()

class stdio(adapter):
    """
    stdio adapter

    Used to read/write points from standard IO which includes the stdin,
    stdout and stderr, but can also be used to read/write points to a
    file on the filesystem
    """

    name = 'stdio'

    stdout = sys.stdout
    stdin = sys.stdin

    def __init__(self,
                 format='jsonl',
                 file=None,
                 append=False,
                 strip_ansi=False,
                 compression=None,
                 **kwargs):
        self.streamer = streamers.get_streamer(format, **kwargs)
        self.file = file
        self.append = append
        self.strip_ansi = strip_ansi
        self.compression = compression

        self.output = None

    def read(self):
        if self.file is None:
            input_stream = InputStream(stdio.stdin,
                                       strip_ansi=self.strip_ansi,
                                       compression=self.compression)

            for point in self.streamer.read(input_stream):
                yield [Point(**point)]

        else:
            if util.IS_PY2:
                encoding = None

            else:
                encoding = _DEFAULT_ENCODING

            with codecs.open(self.file, 'r', encoding=encoding) as stream:
                stream = InputStream(stream,
                                     strip_ansi=self.strip_ansi,
                                     compression=self.compression)

                for point in self.streamer.read(stream):
                    yield [Point(**point)]

    def write(self, points):
        if self.output is None:
            if self.file is None:
                self.output = OutputStream(stdio.stdout,
                                           compression=self.compression)
            else:
                if self.append:
                    mode = 'a'

                else:
                    mode = 'w'

                if util.IS_PY2:
                    encoding = None

                else:
                    encoding = _DEFAULT_ENCODING

                output = codecs.open(self.file, mode, encoding=encoding)
                self.output = OutputStream(output, compression=self.compression)

        self.streamer.write(self.output, points)

    def eof(self):
        if self.output is not None:
            self.streamer.eof(self.output)
            self.output.close()
