# write

The `write` sink is responsible for handling points between **flume** and
an [adapter](../adapters/). The main reason this model is that the `write`
source can handle some of the common tasks that adapters would otherwise
have to implement themselves.

```python
...
| write(adapter,
        batch=-1)
```

Argument  | Description                                                                            | Required?
--------- | -------------------------------------------------------------------------------------- | :---------
adapter   | name of the [adapter](../adapters/) to write to                                        | Yes, default: `None`
batch     | batch size to use when handing points to the adapter, default is to send as we receive | No, default: `-1`
