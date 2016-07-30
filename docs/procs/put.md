# put

The `put` proc is used to add fields to point in the current stream.

```python
...  | put(*field_assignments) | ...
```

Argument           | Description                                     | Required?
------------------ | ----------------------------------------------- | :---------
*field_assignments | list of field assignments to make to each point | No, default: `None`

A field assignment can be as simple as `foo='bar'` or can also be an assignment
to a [reducer](reduce/reducers/) such as `foo=count()`.

# add a count field

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
