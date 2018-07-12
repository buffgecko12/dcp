import datetime
from django.utils.timezone import get_current_timezone

from psycopg2.extras import DateTimeTZRange

def format_timestamp_db(timestamp, formatstring = '%d/%m/%Y', localizeFlag = True):
    mytimestamp = datetime.datetime.strptime(timestamp, formatstring)
    
    if(localizeFlag):
        tz = get_current_timezone()
        mytimestamp = tz.localize(mytimestamp)

    return mytimestamp

def format_timestamp_range_db(timestamprange, formatstring, localizeFlag = True, boundstring = '[]'):

    mystarttimestamp = format_timestamp_db(timestamprange[0], formatstring, localizeFlag)
    myendtimestamp = format_timestamp_db(timestamprange[1], formatstring, localizeFlag)
    
    return DateTimeTZRange(mystarttimestamp, myendtimestamp, boundstring) # Convert to Postgres native tstzrange type

def display_timestamp(timestamp, formatstring = "%d/%m/%Y"):

    return str(timestamp.strftime(formatstring))

def display_timestamp_range(timestamprange, formatstring = "%d/%m/%Y"):

    return display_timestamp(timestamprange.lower, formatstring) + ' - ' + \
           display_timestamp(timestamprange.upper, formatstring)

    return str(timestamprange.lower.strftime(formatstring)) + ' - ' + \
           str(timestamprange.upper.strftime(formatstring))
           
def get_current_timestamp_db():
    return format_timestamp_db(datetime.datetime.now())