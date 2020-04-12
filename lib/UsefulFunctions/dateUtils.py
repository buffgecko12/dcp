from datetime import datetime
from django.utils.timezone import get_current_timezone
from psycopg2.extras import DateTimeTZRange

def convert_date_to_timestamp_db(date, localizeFlag=True):
    mytimestamp = datetime.combine(date, datetime.min.time())

    if localizeFlag:
        tz = get_current_timezone()
        mytimestamp = tz.localize(mytimestamp)

    return mytimestamp

# Functions to convert to native DB types
def format_timestamp_range_db(starttimestamp, endtimestamp, formatstring="%d/%m/%Y", localizeFlag=True, boundstring='[]'):

    mystarttimestamp = convert_date_to_timestamp_db(starttimestamp, localizeFlag)
    myendtimestamp = convert_date_to_timestamp_db(endtimestamp, localizeFlag)

    return DateTimeTZRange(mystarttimestamp, myendtimestamp, boundstring) # Convert to Postgres native tstzrange type

def format_timestamp_string_db(timestamp, formatstring='%d/%m/%Y', localizeFlag=True):
    mytimestamp = datetime.strptime(timestamp, formatstring)

    if localizeFlag:
        tz = get_current_timezone()
        mytimestamp = tz.localize(mytimestamp)

    return mytimestamp

def format_timestamp_range_string_db(timestamprange, formatstring, localizeFlag=True, boundstring='[]'):

    mystarttimestamp = format_timestamp_string_db(timestamprange[0], formatstring, localizeFlag)
    myendtimestamp = format_timestamp_string_db(timestamprange[1], formatstring, localizeFlag)

    return DateTimeTZRange(mystarttimestamp, myendtimestamp, boundstring) # Convert to Postgres native tstzrange type

# Functions to format timestamps for display
def display_timestamp(timestamp, formatstring="%d/%m/%Y"):

    return str(timestamp.strftime(formatstring))

def display_timestamp_range(timestamprange, formatstring="%d/%m/%Y"):

    return display_timestamp(timestamprange.lower, formatstring) + ' - ' + \
           display_timestamp(timestamprange.upper, formatstring)

def get_current_timestamp_db():
    return format_timestamp_string_db(datetime.datetime.now())
