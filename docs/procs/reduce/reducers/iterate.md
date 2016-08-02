# iterate

The `iterate` reducer will iterate through the values in the list it was given
and cycle through those as to "decorate" your data with values from that list.

# labeling points

```python
from flume import *

(
    emit(limit=10, start='2015-01-01')
    | put(label=iterate(['a','b','c']))
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"time": "2015-01-01T00:00:00.000Z", "label": "a"}
{"time": "2015-01-01T00:00:01.000Z", "label": "b"}
{"time": "2015-01-01T00:00:02.000Z", "label": "c"}
{"time": "2015-01-01T00:00:03.000Z", "label": "a"}
{"time": "2015-01-01T00:00:04.000Z", "label": "b"}
{"time": "2015-01-01T00:00:05.000Z", "label": "c"}
{"time": "2015-01-01T00:00:06.000Z", "label": "a"}
{"time": "2015-01-01T00:00:07.000Z", "label": "b"}
{"time": "2015-01-01T00:00:08.000Z", "label": "c"}
{"time": "2015-01-01T00:00:09.000Z", "label": "a"}
```
