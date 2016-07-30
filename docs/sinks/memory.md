# memory

The `meory` sink is used primarily for testing but it does allow you to store
the points that arrive at the sink in an array.

```python
...
| memory(results)
```

Argument  | Description                                                   | Required?
--------- | ------------------------------------------------------------- | :---------
results   | a **Python** list where all of the points will be appended to | Yes, default: `None`
