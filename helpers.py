import re
import logging

from datetime import datetime
from datetime import date
from datetime import timedelta

def is_good_email(email):
    if len(email) > 5: #Shortest possible email address: a@t.co
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

def is_good_name( name ):
    if name != '':
        if re.match( '[A-Za-z]', name ):
            return True
    return False

def triv_today( include_time = False ):
    
    today = datetime.today()
    if not include_time:
        today = datetime.date( today )
    
    # Is today Saturday?
    if today.weekday() == 5:
        today -= timedelta( days = 1 ) # Make it Friday
    
    # Is today Sunday?
    elif today.weekday() == 6:
        today -= timedelta( days = 2 ) # Make it Friday
    
    return today

def to_date( date_time ):
    if date_time:
        return datetime.date( date_time )
    else:
        return None
