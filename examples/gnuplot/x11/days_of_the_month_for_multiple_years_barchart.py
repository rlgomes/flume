from flume import *

(
    (
        emit(limit=366, start='2000-01-01', every='1 day'),
        emit(limit=365, start='2001-01-01', every='1 day')
    )
    | reduce(days=count(), every='1 month', month=date.month('time'), year=date.year('time'))
    | barchart('gnuplot', series='year', category='month', value='days', terminal='x11')
).execute()
