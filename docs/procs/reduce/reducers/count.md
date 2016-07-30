# count

The `count` reducer simply counts the number of points that have passed
through this point in the pipeline.

# counting points

```python
from flume import *

(
    emit(limit=10, start='2015-01-01')
    | reduce(count=count())
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"count": 10, "time": "2015-01-01T00:00:00.000Z"}
```
