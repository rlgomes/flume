# remove

The `remove` proc is used to remove only the field names specified from every
point in the stream.

```python
...  | remove(*fieldnames) | ...
```

Argument    | Description                                 | Required?
----------- | ------------------------------------------- | :---------
*fieldnames | list of field names to remove in each point | No, default: `None`

# remove just the time field

```python
from flume import *

(
    emit(limit=5)
    | put(count=count())
    | remove('time')
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
