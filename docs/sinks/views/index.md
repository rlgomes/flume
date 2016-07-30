# views

Views are an abstraction that allow us to have different implementations for
visualizing our [barchart](../barchart), [linechart](../linechart), etc. sinks
depending on the current need. Currently supported views:

  * [gnuplot](gnuplot/)
  * [pygal](pygal/)
 
# write your own

You can quite easily write your own **view** implementation by extending from
the **flume.sinks.views.base.base** class and then implementing the following
methods:

  * **render(self, chart_type, data)** where the chart_type can currently be
    one of `barchart`, `linechart` or `timechart` and the data is a dictionary
    that maps a series name to the (x,y) pairs that represent it.
    * linechart - the series names match to lines on the chart where the x,y
                  values are the pairs in the list.
    * timechart - the series names match to lines on the chart where the x,y
                  values are the pairs in the list and x is a datetime object.
    * barchart - the series names are the names of the set of bars that have a
                 height of y for the x (may or may not be a datetime object)
                 multiple series represent multiple bars for the same value of x.

For an example checkout the source of the
[gnuplot](https://github.com/rlgomes/flume/blob/master/flume/sinks/views/gnuplot.py)
or [pygal](https://github.com/rlgomes/flume/blob/master/flume/sinks/views/pygalview.py)
views.

The render method may be called many times with intermediate results that
contain the data up to this point and the view implementation must deal with
this how it sees fit such as re-rendering the whole output or simply redrawing
the data that changed.
