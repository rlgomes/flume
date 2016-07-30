"""
timechart sink
"""

from flume import logger
from flume import sink
from flume.sinks.views import get_view


class timechart(sink):

    name = 'timechart'

    def __init__(self,
                 view,
                 series='name',
                 yvalue='value',
                 **kwargs):
        sink.__init__(self)
        self.series = series
        self.yvalue = yvalue
        self.view = get_view(view, **kwargs)

    def loop(self):
        series = {}

        had_data = False
        while self.running:
            points = self.pull()

            has_data = False
            for point in points:
                if 'time' not in point.keys():
                    logger.warn('skipping point without `time` field: %s' % point)
                    continue

                if self.series not in point:
                    logger.warn('unable to find series field "%s" in point' % self.series)
                    name = 'unknown'

                else:
                    name = point[self.series]

                if name not in series:
                    series[name] = []

                has_data = True
                had_data = True
                series[name].append((point.time, point[self.yvalue]))

            if has_data:
                self.view.render(self.name, series)

        if not had_data:
            logger.warn('no data to render')
