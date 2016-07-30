# Examples

There are a few examples under the *examples* directory that highlight a few
simple uses for **flume**. They can all be executed by simply using **python**
and producing some output you can view.

## Barchart showing the days of the month for 2016

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

## Top 5 spammers of syslog

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

## Parse a syslog file and write it to elasticsearch

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
