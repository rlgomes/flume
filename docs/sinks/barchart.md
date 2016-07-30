# barchart

The `barchart` sink is will attempt to render a barchart using an underlying
[view](views/) which can be one of a few different view implementations. The
reason for having the `barchart` sink is to abstract some of the stream 
manipulation code into single place and have the [views](views/) handle the
rendering of the already processed data.

```python
...
| barchart(view,
           series='name',
           category='time',
           value='value',
           **kwargs)
```

Argument  | Description                                                    | Required?
--------- | -------------------------------------------------------------- | :---------
view      | name of the [view](views/) to render the barchart through      | Yes, default: `None`
series    | field name of the individual series (ie bars on the chart)     | No, default: `name`
category  | field name of the values the x-axis represents                 | No, default: `time`
value     | field name of the values the y-axis represents (ie bar height) | No, default: `value`
**kwargs  | additional keyword arguments passed to the underlying view     | No, default: `None`
