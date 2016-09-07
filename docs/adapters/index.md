# adapters

Adapters are the way you can get data in and out of the **flume** pipeline.
There are a set of built in ones that you can read about in the following 
sections and you can also register your own adapter which we'll dive into
how the current API for that works as well below.

## built-in

 * [elastic](/adapters/elastic/)
 * [http](http/)
 * [stdio](stdio/)

## write your own

Writing your own adapter is encouraged as there's no way we'd ever have
an adapter for every possible storage at this point in the development of
**flume**. We also look forward to accepting any adapters written into the
core of **flume** as to better share with the community.

To write your own adapter you need to extend from the class
**flume.adapters.adapter.adapter** and then implement the methods:

  * **name** you must define the name of your adapter with a class level
        attribute called name

  * **__init__(self, ...)** where you initialize your adapter and accept all of
        the keywords your read/write handlers are going to handle.

  * **read(self)**: read method will handle reading points from your backend
        that match the criteria identified by the arguments to your **__init__**
        method and will yield those from the **read** method until there's
        nothing left

  * **write(self, points)** writes the points given to the underlying backend
        and returns from this method once they've all been written out.

  * **eof(self)** called when there are no more points to write to the adapter
        and you can proceed to close off any connections to your backend.

  * **optimize(self, child)** this method is called before the `read` source
        executes and allows the adapter to take a downstream operation such as
        `head`, `tail`, `reduce` and run it within the adapter's engine where the
        data resides and by doing so optimize the **flume** program greatly since
        we don't have to read all the data into **flume** and process it there.
        There's a section below dedicated to explaining how to handle
        optimizations within your own adapter. 

Now that you've written your adapter you can register it using the
**register_streamer(cls)** which will register your adapter with the name
specified by the class level attribute `name`.

## optimizations

Optimizations are the way that **flume** takes a pipeline of operations and
figures out which ones can be executed on the backend (closer to where the data
resides) so that you don't have to transport data from its source to where the
**flume** pipeline is executing in order to compute something on that data or
make a decision about it. With that said the `optimize` method on the adapter
allows you to see what is downstream from the adapter before the adapter starts
running.

As an example the simplest thing to optimize in an adapter is when the following
proc is the [head](../procs/head/) proc then you can simply set a limit
internally in your adapter and stop reading data once you've reached the desired
first N values. This may not seem like much but can save a lot of time if you
were to only need the top 100 values but had 1000 of them to read from a backend
and would simply stop much earlier pulling irrelevant points from the backend.

Have a look at how we implemented the `optimize` method for
[elastic](https://github.com/rlgomes/flume/blob/master/flume/adapters/elastic/node.py)
and 
[stdio](https://github.com/rlgomes/flume/blob/master/flume/adapters/stdio.py)
to get a simple view of how optimization can be done.
