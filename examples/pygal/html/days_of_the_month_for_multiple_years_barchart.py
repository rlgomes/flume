from flume import *

(
    (
        emit(limit=366, start='2000-01-01', every='1 day'),
        emit(limit=365, start='2001-01-01', every='1 day')
    )
    | reduce(days=count(), every='1 month', month=date.month('time'), year=date.year('time'))
    | barchart('pygal', series='year', category='month', value='days', format='html')
).execute()
