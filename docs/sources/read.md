# read

The `read` source is responsible for handling points between
[adapters](../adapters/) and the rest of the **flume** pipeline. The main
reason this model is that the `read` source can handle some of the common
tasks that adapters would otherwise have to implement themselves.

```python
read(adapter,
     time='time') | ...
```

Argument  | Description                                          | Required?
--------- | ---------------------------------------------------- | :---------
adapter   | the name of the [adapter](../adapters/) to read from | Yes, default: `None`
time      | the name of the field that contains the `time` value | No, default: `time`
