# syslog

A collection of syslog utilities that make reading from syslog a whole lot
easier.

## syslog source

```python
syslog(logfile=None,
       path='/var/log/') | ...
```

Argument  | Description                                                          | Required?
--------- | -------------------------------------------------------------------- | :---------
logfile   | the name of the exact syslog file to read (ie /var/log/syslog.7.gz   | No, default: `None`
path      | the path where the syslog files are located (including gzipped ones) | No, default: `/var/log/`

When you don't set the `logfile` we end up figuring out what syslog files are
there and reading through all in order and also handling compression along the
way for the older syslog files that were rotated and compressed.

## calculate syslog lines per day

```bash
flume "syslog() | reduce(count=count(), every='1 day') | write('stdio')"
```

**example output:**
```bash
> flume "syslog() | reduce(count=count(), every='1 day') | write('stdio')"
{"count": 1440, "time": "2016-08-08T08:50:46.000Z"}
{"count": 2133, "time": "2016-08-09T08:50:46.000Z"}
{"count": 1166, "time": "2016-08-10T08:50:46.000Z"}
{"count": 2034, "time": "2016-08-11T08:50:46.000Z"}
{"count": 2197, "time": "2016-08-12T08:50:46.000Z"}
{"count": 1409, "time": "2016-08-13T08:50:46.000Z"}
{"count": 644, "time": "2016-08-14T08:50:46.000Z"}
{"count": 2763, "time": "2016-08-15T08:50:46.000Z"}
```

Or on a [barchart](../sinks/barchart/) using [gnuplot](../sinks/views/gnuplot/):

```bash
flume "syslog() | reduce(value=count(), every='1 day', name='syslog lines', time=date.strftime('time', '%Y-%m-%d')) | barchart('gnuplot')"
```

Which produces for the syslog data on my system:

```bash
     +----+----------+-----------+----------+-----------+----------+--------+-----------+-----+
     |    +          +           +          +           +          +        +   syslog lines  |
     |                                                                                        |
3000 ++                                                                                      ++
     |                                                                               ******   |
2500 ++                                                                              *    *  ++
     |                                                                               *    *   |
     |             ******                            ******                          *    *   |
2000 ++            *    *                 ******     *    *                          *    *  ++
     |             *    *                 *    *     *    *                          *    *   |
     |             *    *                 *    *     *    *                          *    *   |
1500 ++ ******     *    *                 *    *     *    *     ******               *    *  ++
     |  *    *     *    *                 *    *     *    *     *    *               *    *   |
     |  *    *     *    *      ******     *    *     *    *     *    *               *    *   |
1000 ++ *    *     *    *      *    *     *    *     *    *     *    *               *    *  ++
     |  *    *     *    *      *    *     *    *     *    *     *    *     ******    *    *   |
 500 ++ *    *     *    *      *    *     *    *     *    *     *    *     *    *    *    *  ++
     |  *    *     *    *      *    *     *    *     *    *     *    *     *    *    *    *   |
     |  * +  *     * +  *      * +  *     * +  *     *  + *     *  + *     *  + *    *  + *   |
   0 ++-******-----******------******-----******-----******-----******-----******----******--++
       2016-08-08 2016-08-10 2016-08-11 2016-08-12 2016-08-13 2016-08-14 2016-08-14 2016-08-15
```
