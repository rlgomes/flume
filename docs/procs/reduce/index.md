# reduce

The `reduce` proc is used to calculate reductions over the stream of points
using [reducers](reducers/) and a few arguments to get the desired calculation
done.

```python
...  | reduce(every=moment.forever(),
              reset=True,
              by=None,
              *field_assignments) | ...
```

Argument           | Description                                                              | Required?
------------------ | ------------------------------------------------------------------------ | :---------
every              | the interval at which to compute the reduction over.                     | No, default: `moment.forever()`
reset              | specifies if we should reset the reducers at the end of `every` interval | No, default: `True`
by                 | specifies the list of fields to calculate the reductions over            | No, default: `time`
*field_assignments | list of field assignments to make to each point                          | No, default: `None`

A field assignment can be as simple as `foo='bar'` or can also be an assignment
to a [reducer](reduce/reducers/) such as `foo=count()`.

# count days in each month

```python
from flume import *

(
    emit(limit=365, start='2015-01-01', every='1d')
    | reduce(count=count(), every='1 month')
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"count": 31, "time": "2015-01-01T00:00:00.000Z"}
{"count": 28, "time": "2015-02-01T00:00:00.000Z"}
{"count": 31, "time": "2015-03-01T00:00:00.000Z"}
{"count": 30, "time": "2015-04-01T00:00:00.000Z"}
{"count": 31, "time": "2015-05-01T00:00:00.000Z"}
{"count": 30, "time": "2015-06-01T00:00:00.000Z"}
{"count": 31, "time": "2015-07-01T00:00:00.000Z"}
{"count": 31, "time": "2015-08-01T00:00:00.000Z"}
{"count": 30, "time": "2015-09-01T00:00:00.000Z"}
{"count": 31, "time": "2015-10-01T00:00:00.000Z"}
{"count": 30, "time": "2015-11-01T00:00:00.000Z"}
{"count": 31, "time": "2015-12-01T00:00:00.000Z"}
```
