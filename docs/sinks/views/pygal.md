# pygal

The `pygal` view is a view implementation that can render the various views
that **flume** supports (ie barchart, linechart and timechart) using
[pygal](http://www.pygal.org/) which has the ability to render those
charts on a file or even in a [jupyter-notebook](http://jupyter.org/)

```python
...
| chart_type('pygal',
             title='',
             width=1280,
             height=1024,
             filename=None,
             format='png')
```

where chart_type can be [barchart](../barchart), [linechart](../linechart),
[timechart](../timechart).

Argument  | Description                                     | Required?
--------- | ----------------------------------------------- | :---------
title     | title to use on the resulting chart             | Yes, default: `None`
width     | width of the chart to render in pixels          | No, default: `1280`
height    | height of the chart to render in pixels         | No, default: `1024`
filename  | filename to write the output image to (*)       | No, default: `None`
format    | output formats supported: `png` and `html`. (*) | No, default `png` 

(*) optional when in a jupyter-notebook session.
