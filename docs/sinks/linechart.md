# linehart

The `linehart` sink is will attempt to render a line chart using an underlying
[view](views/) which can be one of a few different view implementations. The
reason for having the `linechart` sink is to abstract some of the stream 
manipulation code into single place and have the [views](views/) handle the
rendering of the already processed data.

```python
...
| linechart(view,
            series='name',
            xvalue='time',
            yvalue='value',
            **kwargs)
```

Argument  | Description                                                  | Required?
--------- | ------------------------------------------------------------ | :---------
view      | name of the [view](views/) to render the linechart through   | Yes, default: `None`
series    | field name of the individual series (ie lines on the chart)  | No, default: `name`
xvalue    | field name of the values the x-axis represents               | No, default: `time`
yvalue    | field name of the values the y-axis represents               | No, default: `value`
**kwargs  | additional keyword arguments passed to the underlying view   | No, default: `None`
