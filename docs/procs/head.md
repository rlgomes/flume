# head

The `head` proc is used to keep only the first N points in a stream.

```python
...  | head(how_many) | ...
```

Argument | Description                                     | Required?
-------- | ----------------------------------------------- | :---------
how_many | number of points from the start to let through  | Yes

# keep first 5 points

```python
from flume import *

(
    emit(limit=10)
    | put(count=count())
    | keep('count'
    | head(5)
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"count": 1}
{"count": 2}
{"count": 3}
{"count": 4}
{"count": 5}
```
