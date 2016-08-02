# reducers

reducers are responsible for handling a small piece of computing a value over a
set of points. The way this works is that the reducer will receive individual
update calls with each point that makes it to the [reduce](../../put)
/[put](../../put/).


## built-in

  * [count](count/) 
  * [iterate](iterate/) 
  * [maximum](maximum/) 
  * [minimum](minimum/) 

## write your own

Writing your own reducer is an easy task and should be a common one for various
reducers not yet part of the core **flume** project. To write one you simply
extend from the **flume.reducer** class and implement the following methods:

  * **__init__(self, ...)** make sure to use the constructor to handle passing
                            in the field names from the points that you will 
                            be manipulating.
  * **update(self, point)** this is called for every point that makes it into
                            the current interval of reduction. You should use
                            the names of the fields you stored previously in 
                            the constructor to compute the value you wanted.

  * **result(self)** should return the current value of the reduction being
                     calculated. This means that if you're just counting 
                     the appearance of a field you'd return the current count.

  * **reset(self)** reset is called at the end of `every` interval as defined
                    in the call to the [reduce](../../reduce) proc.
