# seq

The `seq` proc is used to serialize the execution of N **flume** pipelines so
that they execute in the same order that you've passed them to the `seq` proc.

```python
...  | seq(*pipelines) | ...
```

Argument   | Description                                     | Required?
-----------| ----------------------------------------------- | :---------
*pipelines | list of **flume** pipelines to execute serially | Yes


# serialize the execution of two emits

```python
from flume import *

(
    seq(emit(limit=5, every='1s'),
        emit(limit=5, every='0.5s'))
    | write('stdio')
).execute()
```

The above would produce the output:

```json
{"time": "2016-08-12T22:03:06.156Z"}
{"time": "2016-08-12T22:03:07.156Z"}
{"time": "2016-08-12T22:03:08.156Z"}
{"time": "2016-08-12T22:03:09.156Z"}
{"time": "2016-08-12T22:03:10.156Z"}
{"time": "2016-08-12T22:03:11.167Z"}
{"time": "2016-08-12T22:03:11.667Z"}
{"time": "2016-08-12T22:03:12.167Z"}
{"time": "2016-08-12T22:03:12.667Z"}
{"time": "2016-08-12T22:03:13.167Z"}
```

And you'll see how your stream will emit 1 point per second for 5s and then
another 5 points in half that time. Which is a small example of how the `seq`
proc can be useful.
