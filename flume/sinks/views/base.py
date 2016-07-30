"""
base view class
"""
from flume.exceptions import FlumineException

class base(object):

    def render(self, chart_type, data):
        """
        renders the provided data with the desired chart_type chart

        Arguments:
            chart_type - currently supported chart types are:
                linechart, timechart, barchart
            data - a dictionary of series names to lists of (x, y) values,
                like so:
                {
                    "series1": [(0, 0), (1, 1), ...],
                    "series2": [(0, 3), (1, 2), ...],
                    ...
                }

                linechart - the series names match to lines on the chart where
                            the x,y values are the pairs in the list.

                timechart - the series names match to lines on the chart where
                            the x,y values are the pairs in the list and x is
                            a datetime object.

                barchart - the series names are the names of the set of bars
                           that have a height of y for the x (may or may not be
                           a datetime object) multiple series represent multiple
                           bars for the same value of x.
        """
        raise FlumineException('implement me')
