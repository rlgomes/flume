# gnuplot

The `gnuplot` view is a view implementation that can render the various views
that **flume** supports (ie barchart, linechart and timechart) using
[gnuplot](http://www.gnuplot.info/) which has the ability to render those
charts on the console using ASCII art or to an X11 window on Linux which is
somewhat interactive.

```python
...
| chart_type('gnuplot',
             title='',
             width=1280,
             height=1024,
             terminal='dumb')
```

where chart_type can be [barchart](../barchart), [linechart](../linechart),
[timechart](../timechart).

Argument  | Description                                                                  | Required?
--------- | ---------------------------------------------------------------------------- | :---------
title     | title to use on the resulting chart                                          | Yes, default: `None`
width     | width of the chart to render in pixels                                       | No, default: `1280`
height    | height of the chart to render in pixels                                      | No, default: `1024`
terminal  | gnuplot [terminal](http://www.gnuplotting.org/output-terminals/) type to use | No, default: `terminal`
