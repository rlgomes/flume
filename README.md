# flume

**flume** (pronounced *floom*) is a stream processing framework based off of an
older project called [juttle](http://juttle.github.io) from work I did at a previous
company. With **flume** I wanted to be able to use a similar syntax to that of
**juttle** but have the ability to write the stream pipelines in an imperative
programming language such as **python** where you can better coordinate the way
the various pipelines are connected and their order of execution.

This is in no way a production ready solution and actually there are a ton of
features missing which would make this more interesting but I wanted to get
the code up and start sharing it with others to see if there's any interest in
further developing this. I'll continue to tweak and adding things as I have
time and find something I need to accomplish with **flume**.

# installation

## from pypi

```bash
pip install flume
```

## from source

```bash
pip install -e git+git://github.com/rlgomes/flume.git#egg=flume
```

# what is a flume program ?

A **flume** program is pipeline of **flume** nodes that read points from a *source*
and process those points using various **flume** processors which then push the
points to a *sink*. Here's the basic structure of a **flume** program:

    source | proc1 | ... | procN | sink

Now the above is a very simplified view of the world since a **flume** program
can in fact consist of multiple sources, sinks and even split and rejoin
streams of data at various points in the pipeline. Lets start with writing our
first **flume** program where we generate some points using a special source
called **emit** which can emit points to simulate real world data:

```bash
flume "emit(limit=10) | write('stdio')"
```

The above emits 10 points to the sink `write` and pushing those writes through
the **stdio** adapter. The output will look like so (each point is emitted in
realtime):

```json
{"time": "2016-07-17T19:55:40.853Z"}
{"time": "2016-07-17T19:55:41.853Z"}
{"time": "2016-07-17T19:55:42.853Z"}
{"time": "2016-07-17T19:55:43.853Z"}
{"time": "2016-07-17T19:55:44.853Z"}
{"time": "2016-07-17T19:55:45.853Z"}
{"time": "2016-07-17T19:55:46.853Z"}
{"time": "2016-07-17T19:55:47.853Z"}
{"time": "2016-07-17T19:55:48.853Z"}
{"time": "2016-07-17T19:55:49.853Z"}
```

Those points *emit* in realtime one by one since the default value for the
argument `start` is set to *now*, you can set `start` to something such as
`2013-01-01` and it would *emit* those points immediately.

Now let's do something more interesting and read actual data from a real source
such as the syslog file in `examples/grok/syslog` (from the source):

```bash
flume "read('stdio', format='grok', pattern='%{SYSLOGLINE}', file='examples/grok/syslog') | write('stdio')"
```

The above uses quite a few things to achieve the desired result of parsing the
syslog file into data points in the **flume** stream. So there's the **read**
processor which uses the **stdio** adapter to parse the file
`examples/grok/syslog` using the [grok](https://pypi.python.org/pypi/grokpy)
stream parser. We don't have actual a `time` field in our data so we should tell
the `read` processor which field in our data is a time field, like so:

```bash
flume "read('stdio', format='grok', pattern='%{SYSLOGLINE}', file='examples/grok/syslog', time='timestamp') | write('stdio')"
```

We could now do something interesting to our data such as calculating how many
log lines we have per hour in this file. So we have the **reduce** processor
which is used to calculate reductions on our stream. Nothing like an example
to better show case how **reduce** is used:

```bash
flume "read('stdio', format='grok', pattern='%{SYSLOGLINE}', file='examples/grok/syslog', time='timestamp') | reduce(count=count(), every='1h') | write('stdio')"
```

Our command line is getting a little difficult to write on a single command
line so we could use some feature to short hand certain parts of our pipeline.
This is all python code so really there already exists such shorthands by simply
defining new python functions that wrap existing **flume** procesors like so:

```python
def syslog(filename):
    return read('stdio', format='grok', pattern='%{SYSLOGLINE}', file=filename, time='timestamp')
```

And to use your new syslog helper/alias you simply need to create a local
file with the name `.flumerc.py` which can contain utilities you can use
when running the **flume** command line tool. The `.flumerc.py` file should look
like so:

```python
from flume import *

def syslog(file):
    return read('stdio', format='grok', pattern='%{SYSLOGLINE}', file=file, time='timestamp')
```

The `.flumerc.py` file can be used to define anything you'd like to expose
globally for your **flume** command line programs. With the above `.flumerc.py`
file in your current working directory or globally accessible in your home (~/)
directory you can now run the earlier program like so:

```bash
> flume "syslog('examples/grok/syslog') | reduce(count=count(), every='1h') | write('stdio')"
{"count": 27, "time": "2016-07-17T13:59:44.000Z"}
{"count": 1, "time": "2016-07-17T14:59:44.000Z"}
{"count": 110, "time": "2016-07-17T15:59:44.000Z"}
{"count": 8, "time": "2016-07-17T16:59:44.000Z"}
{"count": 118, "time": "2016-07-17T17:59:44.000Z"}
{"count": 10, "time": "2016-07-17T18:59:44.000Z"}
```

That is a lot easier to read and write on the command line and also highlights
the main reason I wanted **flume** to be just an extension of the **python**
runtime where you can simply use existing familiar constructs to build parts
of the **flume** pipeline.

Now what if we actually wanted to get the count of lines generated by each
program writing to the syslog file. This can be easily achieved using the
argument `by` to the **reduce** processor like so:

```bash
> flume "syslog('examples/grok/syslog') | reduce(count=count(), by=['program']) | write('stdio')"
{"count": 178, "program": "kernel", "time": "2016-07-17T13:59:44.000Z"}
{"count": 21, "program": "laptop-mode", "time": "2016-07-17T13:59:44.000Z"}
{"count": 18, "program": "wpa_supplicant", "time": "2016-07-17T13:59:44.000Z"}
{"count": 14, "program": "anacron", "time": "2016-07-17T13:59:44.000Z"}
{"count": 19, "program": "CRON", "time": "2016-07-17T13:59:44.000Z"}
{"count": 3, "program": "cinnamon-screensaver-dialog", "time": "2016-07-17T13:59:44.000Z"}
{"count": 18, "program": "NetworkManager", "time": "2016-07-17T13:59:44.000Z"}
{"count": 3, "program": "console-kit-daemon", "time": "2016-07-17T13:59:44.000Z"}
```

Making the above easier to read we could sort by `count` using the **sort**
processor and get something like so:

```bash
> flume "syslog('examples/grok/syslog') | reduce(count=count(), by=['program']) | sort('count') | write('stdio')"
{"count": 3, "program": "cinnamon-screensaver-dialog"}
{"count": 3, "program": "console-kit-daemon"}
{"count": 14, "program": "anacron"}
{"count": 18, "program": "wpa_supplicant"}
{"count": 18, "program": "NetworkManager"}
{"count": 19, "program": "CRON"}
{"count": 21, "program": "laptop-mode"}
{"count": 178, "program": "kernel"}
```

Which makes it easy to see that the `kernel` is responsible for the majority
of log lines in our syslog file. For those wondering why the `time` field just
disappeared from our output it's because we can't continue to do other things
downstream with points if they're not in chronological order.

At this point I'd be there are a few people saying well I can totally do all of
the above with my **GNU** command line tools. Of course you can and it would
probably look something like so:

```bash
> cat examples/grok/syslog | awk '{print $5}' | sed 's/\[[0-9]*\]//g' | sort | uniq -c | sort -n
      3 cinnamon-screensaver-dialog:
      3 console-kit-daemon:
     14 anacron:
     18 NetworkManager:
     18 wpa_supplicant:
     19 CRON:
     21 laptop-mode:
    178 kernel:
```

It is actually shorter than using **flume** but I doubt you'll find many people
who can read that in a single pass and understand what it does.

The previous section was simply to highlight the usefulness of **flume** and
it barely scratches the surface in terms of what **flume** can let you do when
handling streaming data and also how to output that streaming data to different
types of visualizations and/or pushing the newly calculated data to another
service using the various adapters available.

# examples

There are a few examples under the *examples* directory that highlight a few
simple uses for **flume**. They can all be executed by simply using **python**
and producing some output you can view.

## barchart showing the days of the month for 2016

The following are a few examples of using **flume** to calculate reductions
over a data stream and then rendering a barchart to visualize the crunched
numbers of interest over time.

```bash
python examples/gnuplot/terminal/days_of_the_month_barchart.py

     +----+-----+----+-----+----+-----+----+-----+----+-----+----+-----+----+
     |    +     +    +     +    +     +    +     +    +     +   2015   +    |
  35 ++                                                                    ++
     |                                                                      |
     |   ****       ***        ***        ***   ***        ***       ****   |
  30 ++  *  *       * *   ***  * *   ***  * *   * *  ***   * *  ***  *  *  ++
     |   *  *  ***  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
  25 ++  *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *  ++
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
  20 ++  *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *  ++
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
  15 ++  *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *  ++
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
  10 ++  *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *  ++
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
   5 ++  *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *  ++
     |   *  *  * *  * *   * *  * *   * *  * *   * *  * *   * *  * *  *  *   |
     |   *+ *  *+*  *+*   *+*  *+*   *+*  *+*   *+*  *+*   *+*  *+*  * +*   |
   0 ++--****--***--***---***--***---***--***---***--***---***--***--****--++
         Jan   Feb  Mar   Apr  May   Jun  Jul   Aug  Sep   Oct  Nov   Dec
```

*Note:* A few other intermediate barchart results are printed before this final
barchart.

The above shows how you can use **flume** to calculate how many days in each
month for the year 2015 and then render a barchart using *gnuplot*.

There are a few other examples that produce output in a few other formats:

 * gnuplot x11 `python examples/gnuplot/x11/days_of_the_month_barchart.py`
 * pygal png `python examples/pygal/png/days_of_the_month_barchart.py`
 * pygal html `python examples/pygal/html/days_of_the_month_barchart.py`
 * pygal jupyter-notebook `jupyter-notebook examples/pygal/jupyter-notebooks/days_of_the_month_barchart.ipynb`

All of the above calculate the exact same thing but produce an output in a
slightly different format that may be of use given different scenarios.

## top 5 spammers of syslog

The following example shows you how to use the stdio adapter to read an
example syslog file and then produce the output as a [jsonlines](http://jsonlines.org/)
stream of JSON points showing you the programs that have written the most
amount of lines to that log files:

```bash
> python examples/grok/top_5_syslog_spammers.py
{"count": 178, "program": "kernel"}
{"count": 21, "program": "laptop-mode"}
{"count": 18, "program": "wpa_supplicant"}
{"count": 18, "program": "CRON"}
{"count": 18, "program": "NetworkManager"}
```

## parse a syslog file and write it to elasticsearch

The following example uses the `stdio` adapter parse the syslog lines using
`grok` and then writing those data points to `elasticsearch` so you can later
query elasticsearch from your **flume** program. So before you run this script
you need a locally running instance of elasticsearch which you can very easily
having running with docker like so:

```bash
run -p 9200:9200 elasticsearch:2.3.3
```

Then run the program that writes to **elasticsearch**:

```bash
python examples/elasticsearch/parse_syslog_and_write_into_elasticsearch.py
```

And now you can use **flume** in the command line to simply count how many lines were
ingested like so:

```bash
> flume "read('elastic') | reduce(count=count()) | write('stdio')"
{"count": 274}
```

There are exactly 274 lines in the `examples/grok/syslog` file provided.

# development

All contributions are welcome! File an issue on anything you'd like to see
added or open a pull request with fixes or new features you'd wanted added to
**flume**.

## running tests

The **flume** tests are broken into unittests and integration tests with the
following directory structure:

```
  test/unit
  test/integration
```

They can easily be executed with the *Makefile* running:

```bash
make unit
```

or

```bash
make integration
```

## running coverage check

To run the same check we run in Travis to make sure that code coverage is above
90% simple run:

```bash
make coverage
```
