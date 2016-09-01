# funcr

The `funcr` reducer allows you to apply any operation to a field in the
**flume** stream by creating a reducer dynamically.

```python
... | [put|reduce](value=funcr(function)(fieldname)) | ...
```

Argument  | Description                                          | Required?
--------- | ---------------------------------------------------- | :---------
function  | function name or lambda expression                   | Yes
fieldname | fieldname to apply the function to at streaming time | Yes

# count by increments of 0.1

```python
from flume import *

(
    emit(limit=10, start='2015-01-01')
    | put(count=count())
    | put(count=funcr(lambda value: value / 10.0)('count'))
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"count": 0.1, "time": "2015-01-01T00:00:00.000Z"}
{"count": 0.2, "time": "2015-01-01T00:00:01.000Z"}
{"count": 0.3, "time": "2015-01-01T00:00:02.000Z"}
{"count": 0.4, "time": "2015-01-01T00:00:03.000Z"}
{"count": 0.5, "time": "2015-01-01T00:00:04.000Z"}
{"count": 0.6, "time": "2015-01-01T00:00:05.000Z"}
{"count": 0.7, "time": "2015-01-01T00:00:06.000Z"}
{"count": 0.8, "time": "2015-01-01T00:00:07.000Z"}
{"count": 0.9, "time": "2015-01-01T00:00:08.000Z"}
{"count": 1.0, "time": "2015-01-01T00:00:09.000Z"}
```
