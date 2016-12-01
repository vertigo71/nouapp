import logging
from pytz import timezone


# print a dictionary into a logger 
def logdict(d, logger, depth=0):
    for k, v in d.items():
        if isinstance(v, dict):
          logdict(v, logger, depth+2)
        else:
          logger.info("%s%s : %s", " "*depth, k, v)


# add TimeZone to a datetime
# returns a datetime
def addtz( dt, tz):
    return timezone(tz).localize(dt)

# convert a datetime to a rfc3339 string
# returns a rfc3339 string
# 1996-12-19T16:39:57-08:00          
def datetime2rfc3339(dt, tz):
    return addtz(dt,tz).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    
    
    
    
