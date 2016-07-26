from flume import *

(
    emit(limit=365, start='2015-01-01', every='1 day')
    | reduce(days=count(), every='1 month', month=date.month('time'), year=date.year('time'))
    | barchart('gnuplot', series='year', category='month', value='days', terminal='x11')
).execute()
