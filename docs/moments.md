# moments

A moment (**from flume import moment**) is how you can refer to a specific date
in time or a duration using a human friendly expressions. Further details on
how to express each one of these in the following sections.

## date

A moment date is a human friendly expression that defines a moment in time. For
example if you wanted to refer to an exact date in time you would simply use
the [ISO8601](https://en.wikipedia.org/wiki/ISO_8601) format, like any of the
following examples:

    '2001-01-01T00:00:00.000Z'
    '1998-07-03T02:00:00.000Z'
    '2001-03-02'

You can also express dates in the following formats:

    'Sat Oct 11 17:13:46 UTC 2003'
    'next Saturday'
    'last Friday at 2PM'
    'one hour ago'

With the above you can see how its useful to be able to express dates in a more
human friendly manner. All dates are converted to a **Python**
[datetime](https://docs.python.org/2/library/datetime.html) object.

## duration

Durations are also useful to express in a more human friendly format since
being able to express durations like so:

    '2 seocnds'
    '45 minutes'
    '1 hour 30 minutes'
    '3 months'

And knowing that **flume** will figure out that the `3 months` expression
should be calculated taking into account the exact moment in time that the
stream is processing and calculating the exact distance for those 3 months
to pass. To better understand if you calculate `3 months` from January the 1st
on a non leap year then you would end up with a duration of 31 + 28 + 31 days,
but on a leap year you'd end up with 31 + 29 + 31 days.  All durations are
converted to a [timedelta](https://docs.python.org/2/library/datetime.html#timedelta-objects)
object.
