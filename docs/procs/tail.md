# tail

The `tail` proc is used to keep only the last N points in a stream.

```python
...  | tail(how_many) | ...
```

Argument | Description                                   | Required?
-------- | --------------------------------------------- | :---------
how_many | number of points from the end to let through  | Yes

# keep last 5 points

```python
from flume import *

(
    emit(limit=10)
    | put(count=count())
    | keep('count'
    | tail(5)
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"count": 6}
{"count": 7}
{"count": 8}
{"count": 9}
{"count": 10}
```
