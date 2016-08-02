# overview

## basics

A **flume** program is pipeline of **flume** nodes that read points from a *source*
and process those points using various **flume** procs (short for processors)
which in turn push the points to a *sink*. Here's the basic structure of a
**flume** program:

    source | proc1 | ... | procN | sink

Now the above is a very simplified view of the world since a **flume** program
can in fact consist of multiple sources, sinks and even split and rejoin
streams of data at various points in the pipeline. For example you can read
from multiple sources and merge the points like so:

    (source1 ; source2 ; source3) | ... | sink

The parenthesis are used to expression parallel pipelines in **flume** and at
the end of the parenthesis block all those points are merged together in order
unless you use one of set procs such as [union](procs/union.md),
[intersect](procs/intersect.md) or [diff](procs/diff.md) to create the new 
stream applying the specific set operation you want applied. This same 
ability to handle `N` sources allows you to also split the stream at any point
in your pipeline. So here's another somewhat less abstract example:

    source
    | (
        filter('value % 2 == 0') | put(even=count()),
        filter('value % 2 != 0') | put(odd=count())
    ) | sink

The above wouldn't be possible to calculate unless we split the stream since
we have to eliminate things from the stream on either side that are in direct
conflict with the other type of calculation involved. In a more imperative 
way of doing this you'd also split the stream by keeping the intermediate value
in two different variables tracking the odd vs even count.

## streams and reducers

**Flume** can handle streams of points with and without a valid time field. The
main reason you want a time field is calculate reductions over your stream of
points. Without a time field you can do things such as adding fields to your
data and/or joining with other streams to decorate those with missing
information. Lets start by first diving into what a stream with a `time` field
looks like:

```
emit(limit=10) | write('stdio')
```

The previous **flume** program uses the [emit](sources/emit) proc to create
points that contain just a `time` field starting as of right now and creating
a point every second until we've "emitted" a total of 10 points. The output
of running the above with the **flume** CLI looks like so:

```bash
> flume "emit(limit=10) | write('stdio')"
{"time": "2016-07-30T15:18:15.562Z"}
{"time": "2016-07-30T15:18:16.562Z"}
{"time": "2016-07-30T15:18:17.562Z"}
{"time": "2016-07-30T15:18:18.562Z"}
{"time": "2016-07-30T15:18:19.562Z"}
{"time": "2016-07-30T15:18:20.562Z"}
{"time": "2016-07-30T15:18:21.562Z"}
{"time": "2016-07-30T15:18:22.562Z"}
{"time": "2016-07-30T15:18:23.562Z"}
{"time": "2016-07-30T15:18:24.562Z"}
```

The output format used is [jsonlines](http://jsonlines.org/) which allows for a
true stream of data since each line represents a valid **JSON** object. The 
previous stream has a `time` field so we can used the [reduce](procs/reduce)
proc to calculate time aligned reductions. This is done by specifying the 
reduction we want to calculate and the new field we want to create with the
result of that reduction. Here's a simple example:

```bash
> flume "emit(limit=10) | reduce(count=count()) | write('stdio')"
{"count": 10, "time": "2016-07-30T15:22:30.033Z"}
```

Now the [reducer](reducer/reducers/) used was [count](reduce/reducers/count)
which simply calculates for a given interval the number of points that passed
through the [reduce](procs/reduce/) proc during that time. The interval itself
is set with the argument `every` to the **reduce** proc and in this case since
we didn't set it to anything we basically said to reduce over the full length
of our stream.
