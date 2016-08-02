# filter expressions

Filter expressions allow the end user to decide which points in a stream make
it past a certain point. Currently some adapters expose the filter expression
directly in the call to read/write so you can filter points in the backend
before they make it into the **flume** pipeline. You can also filter at any
point in the pipeline using the [filter](procs/filter) proc.

Currently we only support a single format for filter expressions and that is
a string containing a **Python** logical expression which can refer to any
field contained in the current point of the stream by name. So some like so:

    field1 > 0

Would be a filter expression where for each point in the stream that has the
field with the name `field1` would only make it farther down the pipeline if
its value was greater than 0. With this freedom to use any **Python** logical
expression you can do even more fancier things:

    field1 in [1, 3, 5]
    foo > bar + bananas
    etc.

Now while you can do almost anything when creating the filter expression due to
the freedom of expressing such expressions in **Python**, in the future when we
start optimizing said filters and sending them back to the backend we obviously
can't send all kinds of expressions. When that time comes we'll document
clearly which backends support which types of expression optimization.
