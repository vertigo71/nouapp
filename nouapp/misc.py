import logging, sys
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
    
    
def query_yes_no(question, default=None):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes", "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '{}'".format( default) )

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

    
    
