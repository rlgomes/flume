# stdio adapter

The `stdio` adapter can be used to read and write to and from any file input.
This includes the stdin/stdout of a process but can also mean reading/writing
from a file on the file system.

## read

Reading from `stdio` is done using the [read](../sources/read) source with the
following options available at this time:

```python
read('stdio',
     format='jsonl',
     file=None,
     strip_ansi=False,
     time='time') | ...
```

Argument    | Description                                                                 | Required?
----------- | --------------------------------------------------------------------------- | :---------
format      | format specifier used to pick a different kind of [streamer](streamers/)    | No, default: `jsonl`
file        | filename to read from, when not specified we read from STDIN                | No, default: `None`
strip_ansi  | when set to `True` then all ANSI sequences are removed from the input       | No, default: `False`
time        | field name that contains valid timestamp                                    | No, default: `time`

## write

Writing to `stdio` is done using the [write](../sinks/write) sink with the
following options available at this time:

```python
write('stdio',
      format='jsonl',
      file=None,
      append=False,
      time='time') | ...
```

Argument    | Description                                                                 | Required?
----------- | --------------------------------------------------------------------------- | :---------
format      | format specifier used to pick a different kind of [streamer](streamers/)    | No, default: `jsonl`
file        | filename to write to, when not specified we read from STDOUT                | No, default: `None`
append      | boolean that specifies if we should append or not to any existing output    | No, default: `False`
time        | field name that contains valid timestamp                                    | No, default: `time`


## reading data from dmesg

The `dmesg` command has output that looks like so:

```bash
[83281.308572] EXT4-fs (dm-1): re-mounted. Opts: errors=remount-ro,commit=0
[83281.335411] EXT4-fs (sda2): re-mounted. Opts: (null)
[83281.417356] device vboxnet4 entered promiscuous mode
[83281.524426] [drm] RC6 on
[83284.403642] wlan0: authenticate with 10:05:b1:e0:83:20
[83284.414489] wlan0: send auth to 10:05:b1:e0:83:20 (try 1/3)
[83284.420835] wlan0: authenticated
[83284.424327] wlan0: associate with 10:05:b1:e0:83:20 (try 1/3)
[83284.427721] wlan0: RX AssocResp from 10:05:b1:e0:83:20 (capab=0x411 status=0 aid=6)
[83284.430732] wlan0: associated
[83285.900045] psmouse serio2: trackpoint: IBM TrackPoint firmware: 0x0e, buttons: 3/3
```

Luckily we have built in support for parsing data with [grok](https://github.com/garyelephant/pygrok)
which allows us to parse the above using a pattern like so:

    \[\s+%{BASE10NUM:timestamp}\]\s+%{WORD:app}%{GREEDYDATA:message}')

We're going with a simple approach to getting the timestamp as a number and
also the first thing that is not a space becomes the name of the application
that logged the line to the dmesg log. Now with the above expression we can use
the `stdio` adapter to figure out which are the top 5 applications that have
been writing to dmesg:

```python
from flume import *

(
    read('stdio',
         format='grok',
         pattern='\[\s*%{BASE10NUM:timestamp}\]\s+%{NOTSPACE:app}%{GREEDYDATA:message}')
    | reduce(count=count(), by=['app'])
    | sort('count', order='desc')
    | head(5)
    | write('stdio')
).execute()
```

The above is a but crude but gives us some interesting output which shows on my
laptop that the top 5 spammers include:

```bash
> dmesg  | python test.py
{"count": 361, "app": "PM:"}
{"count": 320, "app": "wlan0:"}
{"count": 219, "app": "ata2.00:"}
{"count": 200, "app": "usb"}
{"count": 180, "app": "smpboot:"}
```

Which means my wifi adapter and the power management services spam the dmesg log
the most. The previous execution also shows how the `stdio` adapter handles
reading data directly from the `STDIN` so you can pipe data from other commands
directly to the **Python** process.

## writing CSV data

```python
from flume import *

(
    read('stdio',
         format='grok',
         pattern='\[\s*%{BASE10NUM:timestamp}\]\s+%{NOTSPACE:app}%{GREEDYDATA:message}')
    | write('stdio', format='csv', file='dmesg.csv')
).execute()
```

The above will transform the `dmesg` input provided to this **Python** program
through `STDIN` will be written out in a `CSV` format to the `dmesg.csv` file.
The `CSV` file will contain the columns timestamp, app and message and can be
easily imported into your favorite spreadsheet application
