"""
pygal view
"""

import sys
import tempfile

import pygal

from flume.sinks.views.base import base
from flume.exceptions import FlumineException
from flume import moment

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
  <script type="text/javascript" src="http://kozea.github.com/pygal.js/javascripts/svg.jquery.js"></script>
  <script type="text/javascript" src="http://kozea.github.com/pygal.js/javascripts/pygal-tooltips.js"></script>
    <!-- ... -->
  </head>
  <body>
    <figure>
        %s
    </figure>
  </body>
</html>"""


def is_ipython():
    try:
        return __IPYTHON__
    except:
        return False

class PyGal(base):

    def __init__(self,
                 title='',
                 width=1280,
                 height=1024,
                 filename=None,
                 format='png'):
        self.title = title
        self.width = width
        self.height = height

        if not is_ipython():
            if format not in ['png', 'html']:
                raise FlumineException('supported formats are "html" and "png"')

            if filename is None:
                # save to a temporary file and open with default image viewer
                _, filename = tempfile.mkstemp('.' + format)
                sys.stdout.write('rendering chart to "%s"\n' % filename)
                sys.stdout.flush()

            self.filename = filename

    def render(self, chart_type, data):
        if chart_type == 'linechart':
            chart = pygal.XY(height=self.height,
                             width=self.width,
                             x_label_rotation=45)

            chart.title = self.title

            for series_name in data.keys():
                series = data[series_name]
                chart.add(series_name, series)

        elif chart_type == 'timechart':
            chart = pygal.DateTimeLine(height=self.height,
                                       width=self.width,
                                       x_label_rotation=45,
                                       x_value_formatter=moment.datetime_to_iso8601)

            chart.title = self.title

            for series_name in data.keys():
                series = data[series_name]
                chart.add(series_name, series)

        elif chart_type == 'barchart':
            chart = pygal.Bar(height=self.height, width=self.width)
            chart.title = self.title

            chart.x_labels = [category for (category, _) in data[list(data.keys())[0]]]

            for series_name in data.keys():
                series = [value for (_, value) in data[series_name]]
                chart.add(series_name, series)

        else:
            raise FlumineException('unsupported chart type "%s" for pygal view'
                                   % chart_type)

        if is_ipython():
            from IPython.core.display import display, HTML, clear_output
            clear_output(wait=True)
            display(HTML(chart.render()))

        elif self.filename.endswith('.png'):
            chart.render_to_png(self.filename)

        elif self.filename.endswith('.html'):
            with open(self.filename, 'w') as output:
                output.write(HTML_TEMPLATE % chart.render())
