# timechart

The `timehart` sink is will attempt to render a time chart using an underlying
[view](views/) which can be one of a few different view implementations. The
reason for having the `timechart` sink is to abstract some of the stream 
manipulation code into single place and have the [views](views/) handle the
rendering of the already processed data.

```python
...
| timechart(view,
            series='name',
            yvalue='value',
            **kwargs)
```

Argument  | Description                                                    | Required?
--------- | -------------------------------------------------------------- | :---------
view      | name of the [view](views/) to render the timechart through     | Yes, default: `None`
series    | field name of the individual series (ie lines on the chart)    | No, default: `name`
yvalue    | field name of the values the y-axis represents                 | No, default: `value`
**kwargs  | additional keyword arguments passed to the underlying view     | No, default: `None`
