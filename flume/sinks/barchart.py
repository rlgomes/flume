"""
barchart sink
"""

from flume import logger
from flume import sink
from flume.sinks.views import get_view


class barchart(sink):

    name = 'barchart'

    def __init__(self,
                 view,
                 series='name',
                 category='time',
                 value='value',
                 **kwargs):
        sink.__init__(self)
        self.series = series
        self.category = category
        self.value = value
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

                if name not in series.keys():
                    series[name] = []

                series[name].append((point[self.category], point[self.value]))

            self.view.render('barchart', series)
