from flume import *

(
    emit(limit=180, start='2000-01-01', every='1s')
    | put(name='sin',
          count=count(),
          xvalue=funcr(lambda count: count/10.0)('count'),
          value=math.sin('xvalue'))
    | linechart('gnuplot', xvalue='xvalue', yvalue='value', terminal='x11')
).execute()
