"""
gnuplot view
"""
import os
import subprocess
import tempfile

from datetime import datetime

import blessings

from flume.sinks.views.base import base
from flume.exceptions import FlumineException


class Gnuplot(base):

    def __init__(self,
                 title='',
                 width=1280,
                 height=1024,
                 terminal='dumb',
                 timefmt='%Y/%d/%m-%H:%M:%S'):
        self.title = title
        self.width = width
        self.height = height
        self.terminal = terminal
        self.timefmt = timefmt

        if terminal == 'dumb':
            self.process = None

        else:
            self.process = subprocess.Popen(['gnuplot', '-p'], stdin=subprocess.PIPE)

    def init_terminal(self, min_value, max_value):
        if self.terminal == 'dumb':
            if self.process is not None:
                self.write('exit\n')
                self.process.wait()

            import time
            time.sleep(0.1)
            self.process = subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE)

            terminal = blessings.Terminal()

            self.write('set terminal %s size %d, %d\n' %
                       (self.terminal, terminal.width, terminal.height))

        else:
            self.write('clear\n')
            self.write('set terminal %s size %d, %d\n' %
                       (self.terminal, self.width, self.height))

        max_value = max_value * 1.25
        self.write('set yrange [%g:%g]\n' % (min_value, max_value))

    def write(self, line):
        self.process.stdin.write(line.encode('utf-8'))
        self.process.stdin.flush()

    def render(self, chart_type, data):
        min_value = 0
        max_value = 0
        x_is_time = False

        tmp = tempfile.mkdtemp()
        for series_name in data.keys():
            filename = os.path.join(tmp, '%s.dat' % series_name)

            with open(filename, 'w') as output:
                for (colx, coly) in data[series_name]:

                    if coly > max_value or max_value is None:
                        max_value = coly

                    if coly < min_value or min_value is None:
                        min_value = coly

                    if isinstance(colx, datetime):
                        x_is_time = True
                        date = '%s/%s/%s-%s:%s:%s' % (colx.year, colx.day, colx.month,
                                                      colx.hour, colx.minute, colx.second)
                        output.write('%s\t%s\n' % (date, coly))

                    else:
                        output.write('%s\t%s\n' % (colx, coly))

        self.init_terminal(min_value, max_value)

        if chart_type == 'linechart' or chart_type == 'timechart':
            if x_is_time:

                if chart_type == 'timechart':
                    self.write('set xdata time\n')
                    self.write('set format x "%s"\n' % self.timefmt)
                    self.write('set timefmt "%s"\n' % self.timefmt)

            series_string = ['"%s" using 1:2 with linespoints title "%s"' % \
                             (os.path.join(tmp, '%s.dat' % series_name), series_name)
                             for series_name in data.keys()]

        elif chart_type == 'barchart':
            self.write('set boxwidth 0.8\n')
            self.write('set style fill solid\n')
            self.write('set style data histogram\n')
            self.write('set style histogram cluster gap 1\n')

            series_string = ['"%s" using 2:xtic(1) title "%s"' % \
                             (os.path.join(tmp, '%s.dat' % series_name), series_name)
                             for series_name in data.keys()]

        else:
            raise FlumineException('unsupported chart type "%s" for pygal view'
                                   % chart_type)

        self.write('plot %s\n' % ', '.join(series_string))
