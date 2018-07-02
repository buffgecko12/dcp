import datetime
from django.utils.timezone import get_current_timezone
import ast

from psycopg2.extras import DateTimeTZRange

def format_timestamp(timestamp, formatstring, localizeFlag = True):
    mytimestamp = datetime.datetime.strptime(timestamp, formatstring)
    
    if(localizeFlag):
        tz = get_current_timezone()
        mytimestamp = tz.localize(mytimestamp)

    return mytimestamp

def format_timestamp_range(timestamprange, formatstring, localizeFlag = True, boundstring = '[]'):

    mytimestamprange = ast.literal_eval(timestamprange)

    mystarttimestamp = format_timestamp(mytimestamprange[0], formatstring, localizeFlag)
    myendtimestamp = format_timestamp(mytimestamprange[1], formatstring, localizeFlag)
    
    return DateTimeTZRange(mystarttimestamp, myendtimestamp, boundstring) # Convert to Postgres native tstzrange type