# date

The `date` reducers can be used to easily extract information from existing
datetime fields such as the `time` field. You'll see below how to use each one.

# .year

```python
... | reduce(year=date.year('time')) | ...
```

Converts a `datetime` field value into the string that represents the year, such
as `2016`, `1975`, etc. Can be used both in the [put](../../put/) and
[reduce](../../reduce) processors.

# .fullmonth

```python
... | reduce(fullmonth=date.fullmonth('time')) | ...
```

Converts a `datetime` field value into the string that represents the full
month, such as `January`, `December`, etc. Can be used both in the [put](../../put/) and
[reduce](../../reduce) processors.

# .month

```python
... | reduce(month=date.month('time')) | ...
```

Converts a `datetime` field value into the string that represents the abreviated
month, such as `Jan`, `Dec`, etc. Can be used both in the [put](../../put/) and
[reduce](../../reduce) processors.

# .fullweekday

```python
... | reduce(fullweekday=date.fullweekday('time')) | ...
```

Converts a `datetime` field value into the string that represents the full
weekday, such as `Tuesday`, `Sunday`, etc. Can be used both in the
[put](../../put/) and [reduce](../../reduce) processors.

# .weekday

```python
... | reduce(weekday=date.weekday('time')) | ...
```

Converts a `datetime` field value into the string that represents the abreviated
weekday, such as `Tue`, `Sun`, etc. Can be used both in the [put](../../put/)
and [reduce](../../reduce) processors.

# .strftime

```python
... | reduce(shortdate=date.strftime('time', '%Y/%m/%d')) | ...
```

Converts a `datetime` field value into the format specified using python's
`strftime` format from [here](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior) 
Can be used both in the [put](../../put/) and [reduce](../../reduce) processors.
