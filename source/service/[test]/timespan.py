import datetime
from chengutil import util

ts1 = util.getTimeStamp('2018-08-05 12:00:00')
print(ts1)
ts2 = util.getTimeStamp('2018-08-08 12:00:00')
ts3 = ts2 - ts1
print(ts3)
print(ts3/60/60/24)