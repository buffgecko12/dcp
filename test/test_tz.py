import test_env_setup
import unittest
from UsefulFunctions.dateUtils import format_timestamp_string_db, format_timestamp_range_string_db, format_timestamp_range_db
import datetime

class testTimestamp(unittest.TestCase):
    def test_timestamp_functions(self):
        # Timestamp string to db
        datetime_data = '2018-06-22'
        format1 = '%Y-%m-%d'
        date_object = format_timestamp_string_db(timestamp = datetime_data, formatstring = format1)
        
        # Timestamp range string to db
        datetime_data = ['14/06/2018', '22/06/2018']
        format1 = '%d/%m/%Y'
        date_object = format_timestamp_range_string_db(timestamprange=datetime_data, formatstring=format1)
                
        # Timestamp range to db
        ts1 = datetime.datetime.now()
        ts2 = ts1+ datetime.timedelta(days=1)
        date_object = format_timestamp_range_db(starttimestamp = ts1, endtimestamp=ts2)

if __name__ == '__main__':
    unittest.main() # Run all tests