# installation

Installing **flume** is as simple as any other **Python** package:

```bash
pip install flume
```

At this point you should have the **flume** command line utility which you can
verify like so:

```bash
flume "emit(limit=3) | write('stdio')"
```

Which should produce the following output over the course of 3s:

```json
{"time": "2016-07-29T22:02:03.839Z"}
{"time": "2016-07-29T22:02:04.839Z"}
{"time": "2016-07-29T22:02:05.839Z"}
```
