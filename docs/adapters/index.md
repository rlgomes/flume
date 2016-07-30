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
  *          attribute called name

  * **__init__(self, ...)** where you initialize your adapter and accept all of
                            the keywords your read/write handlers are going to 
                            handle.
  * **read(self)**: read method will handle reading points from your backend
                    that match the criteria identified by the arguments to your
                    **__init__** method and will yield those from the **read** 
                    method until there's nothing left
  * **write(self, points)** writes the points given to the underlying backend
                            and returns from this method once they've all been
                            written out.
  * **eof(self)** called when there are no more points to write to the adapter
                  and you can proceed to close off any connections to your
                  backend.

Now that you've written your adapter you can register it using the
**register_streamer(cls)** which will register your adapter with the name
specified by the class level attribute `name`.
