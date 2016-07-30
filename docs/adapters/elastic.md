# elastic adapter

The elastic adapter can be used to read and write data from a running
[elasticsearch](https://www.elastic.co/) instance. The currently supported versions of elasticsearch that we have integration tests to verify against is 2.3.3 . We'll be adding verification of a view other versions shortly and
if you want to see support for a specific version please let us know on our
github [issues](https://github.com/rlgomes/flume/issues) tracking system.

## read

Reading from the elastic adapter is done using the [read](../sources/read) source
with the following options available at this time:

```python
read('elastic',
     index='_all',
     type='metric',
     host='localhost',
     port=9200,
     time='time',
     filter=None,
     batch=1024) | ...
```

Argument | Description                                      | Required?
-------- | ------------------------------------------------ | :---------
index    | elasticsearch index to read from                 | No, default: `_all`
type     | elasticsearch document type to read              | No, default: `metric`
host     | hostname of the elasticsearch instance           | No, default: `localhost`
port     | port of the elasticsearch instance               | No, default: `9200`
time     | field name that contains valid timestamp         | No, default: `time`
filter   | filter expression to run against the es data (*) | No, default:  `None`
batch    | the read batch size when reading from es         | No, default: `1024`

 * (*) filter expressions are further explained [here](../filter_expressions)

## write

Writing to the elastic adapter is done using the [write](../sinks/write) sink
with the following options available at this time:

```python
... | write('elastic',
            index='_all',
            type='metric',
            host='localhost',
            port=9200,
            time='time',
            filter=None,
            batch=1024)
```

Argument | Description                                  | Required?
-------- | -------------------------------------------- | :---------
index    | elasticsearch index to write to              | No, default: `_all`
type     | elasticsearch document type to write         | No, default: `metric`
host     | hostname of the elasticsearch instance       | No, default: `localhost`
port     | port of the elasticsearch instance           | No, default: `9200`

## writing a few points to elastic

```python
from flume import emit, write

(
    emit(limit=10, start='2013-01-01', every='day')
    | write('elastic', index='test-index')
).execute()
```

To test out the above using a quick elasticsearch instance spun up using docker
just use the following quick command line:

```bash
docker run -p 9200:9200 elasticsearch:2.3.3
```

Then you can execute the program, but there will be no output and you can easily
verify your data was stored to that local instance by hitting:

    http://localhost:9200/test-index/_search

Where the JSON response should have 10 hits and you should be able to see the
`_source` field contains the timestamps from `2013-01-01T00:00:00.000Z` to 
`2013-01-101T00:00:00.000Z` (they're not sorted at this point).

# reading points from elastic

```python
from flume import read, write

(
    read('elastic', index='test-index')
    | write('stdio')
).execute()
```

Which produces the following output:

```bash
> python test.py 
{"time": "2013-01-01T00:00:00.000Z"}
{"time": "2013-01-02T00:00:00.000Z"}
{"time": "2013-01-03T00:00:00.000Z"}
{"time": "2013-01-04T00:00:00.000Z"}
{"time": "2013-01-05T00:00:00.000Z"}
{"time": "2013-01-06T00:00:00.000Z"}
{"time": "2013-01-07T00:00:00.000Z"}
{"time": "2013-01-08T00:00:00.000Z"}
{"time": "2013-01-09T00:00:00.000Z"}
{"time": "2013-01-10T00:00:00.000Z"}
```
