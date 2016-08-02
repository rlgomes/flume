# sort

The `sort` proc is used to sort your points by a specific field (other than
time). When you use `sort` the resulting points have no `time` field
associated.

```python
...  | sort(*fieldnames,
            order='asc',
            limit=100000) | ...
```

Argument    | Description                                                             | Required?
----------- | ----------------------------------------------------------------------- | :---------
*fieldnames | list or tuple of field names to sort the stream by                      | No, default: `time`
order       | `asc` to order ascending and `desc` to order points by descending order | No, default: `asc`
limit       | buffering limit set to avoid running out of memory                      | No, default: `100000`

# sort stream descending by count

```python
from flume import *

(
    emit(limit=5)
    | put(count=count())
    | sort('count', order='desc')
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"count": 5}
{"count": 4}
{"count": 3}
{"count": 2}
{"count": 1}
```
