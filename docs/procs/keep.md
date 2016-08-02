# keep

The `keep` proc is used to keep only the field names specified from every
point in the stream.

```python
...  | keep(*fieldnames) | ...
```

Argument    | Description                               | Required?
----------- | ----------------------------------------- | :---------
*fieldnames | list of field names to keep in each point | No, default: `None`

# keep just the count field

```python
from flume import *

(
    emit(limit=5)
    | put(count=count())
    | keep('count'
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
