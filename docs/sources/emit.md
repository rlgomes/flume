# emit

The `emit` source is primarily used for testing and can be used to generate
points from a specific point in time at a specific interval.

```python
emit(limit=-1,
     every='1s',
     points=None,
     start=None,
     end=moment.end()) | ...
```

Argument  | Description                                                                         | Required?
--------- | ----------------------------------------------------------------------------------- | :---------
limit     | total number of points to emit, when not set emits forever                          | No, default: `-1`
every     | [moments.duration](../moments#duration) specifying the rate at which to emit points | No, default: `1s`
points    | a list of points to emit in order                                                   | No, default: `None`
start     | [moments.date](../moments#date) specifying the exact date in time to start          | No, default: `None`
end       | [moments.date](../moments#date) specifying the exact date in time to stop emitting  | No, default: `moment.end()`

## emitting a point for every day in 2013

```python
from flume import emit, write

(
    emit(limit=365, start='2013-01-01', every='1 day')
    | write('stdio')
).execute()
```
