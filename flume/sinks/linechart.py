"""
linechart sink
"""

from flume import logger
from flume import sink
from flume.sinks.views import get_view


class linechart(sink):

    name = 'linechart'

    def __init__(self,
                 view,
                 series='name',
                 yvalue='value',
                 xvalue='time',
                 **kwargs):
        sink.__init__(self)
        self.series = series
        self.xvalue = xvalue
        self.yvalue = yvalue
        self.view = get_view(view, **kwargs)

    def loop(self):
        series = {}

        while self.running:
            points = self.pull()

            for point in points:
                if self.series not in point:
                    logger.warn('unable to find series field "%s" in point' % self.series)
                    name = 'unknown'
                else:
                    name = point[self.series]

                if name not in series:
                    series[name] = []

                series[name].append((point[self.xvalue],
                                     point[self.yvalue]))

            self.view.render(self.name, series)
