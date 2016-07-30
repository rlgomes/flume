# filter

The `filter` proc is used to apply [filter expression](../filter_expressions)
at any given point in the **flume** pipeline.

```python
...  | filter(expression) | ...
```

Argument   | Description                              | Required?
---------- | ---------------------------------------- | :---------
expression | specifies the filter expression to apply | Yes

# dropping odd numbers

```python
from flume import *

(
    emit(limit=10)
    | put(count=count())
    | filter('count % 2 == 0')
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"count": 2, "time": "2016-08-01T22:28:12.416Z"}
{"count": 4, "time": "2016-08-01T22:28:14.416Z"}
{"count": 6, "time": "2016-08-01T22:28:16.416Z"}
{"count": 8, "time": "2016-08-01T22:28:18.416Z"}
{"count": 10, "time": "2016-08-01T22:28:20.416Z"}
```
