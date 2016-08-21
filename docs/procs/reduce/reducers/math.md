# math

The `math` reducers exposed are the following set of functions from the math 
module in python that can be applied against any of the fields in your **flume**
stream. Mostly we exposed the python `math` module from
[here](https://docs.python.org/2/library/math.html).

## number-theoretic and representation functions

  * `math.ceil(fieldname)`
  * `math.fabs(fieldname)`
  * `math.floor(fieldname)`
  * `math.factorial(fieldname)`
  * `math.fmod(fieldname)`
  * `math.trunc(fieldname)`
  * `math.isinf(fieldname)`
  * `math.isnan(fieldname)`

## power and logarithmic functions

  * `math.exp(fieldname)`
  * `math.expm1(fieldname)`
  * `math.log(fieldname)`
  * `math.log1p(fieldname)`
  * `math.log10(fieldname)`
  * `math.pow(fieldname, power)`
  * `math.sqrt(fieldname)`

## trigonometric functions

  * `math.acos(fieldname)`
  * `math.asin(fieldname)`
  * `math.atan(fieldname)`
  * `math.atan2(fieldname)`
  * `math.cos(fieldname)`
  * `math.sin(fieldname)`
  * `math.tan(fieldname)`

## angular conversion

  * `math.degrees(fieldname)`
  * `math.radians(fieldname)`
