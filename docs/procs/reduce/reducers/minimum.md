# minimum

The `minimum` reducer picks the maximum value of the field provided during the
reduction interval.

# minimum value for a field

```python
from flume import *

(
    emit(limit=10, start='2015-01-01')
    | put(count=count())
    | reduce(minimum=maximum('count'))
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"minimum": 10, "time": "2015-01-01T00:00:00.000Z"}
```
