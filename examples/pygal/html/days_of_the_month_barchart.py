from flume import *

(
    emit(limit=365, start='2015-01-01', every='1 day')
    | reduce(days=count(), every='1 month', month=date.month('time'), year=date.year('time'))
    | barchart('pygal', series='year', category='month', value='days', format='html')
).execute()
