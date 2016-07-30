# diff

The `diff` proc is part of the set operators that can be used to join two
streams back into one but applying some set operator to the items of the
stream. In this case only allow points that don't appear in all of the
inputs.

```python
( ... , ....) | diff(*fieldnames) | ...
```

Argument    | Description                                           | Required?
----------- | ----------------------------------------------------- | :---------
*fieldnames | list or tuple of field names to calculate the diff on | Yes, default: `time`


# diffing two streams

```python
from flume import *

(
    (emit(points=[
        {'time': '2010-01-01T00:00:00.000Z', 'a': 0},
        {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
        {'time': '2010-01-01T00:02:00.000Z', 'a': 2}
    ]),
    emit(points=[
        {'time': '2010-01-01T00:01:00.000Z', 'a': 1},
        {'time': '2010-01-01T00:02:00.000Z', 'a': 2},
        {'time': '2010-01-01T00:05:00.000Z', 'a': 3}
    ]))
    | diff()
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"a": 0, "time": "2010-01-01T00:00:00.000Z"}
{"a": 3, "time": "2010-01-01T00:05:00.000Z"}
```

The only points to come out the other side of the `diff` are the `a==0` and
`a==3` point which are not found in both streams.
