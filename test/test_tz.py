import test_setup
from UsefulFunctions.dateUtils import format_timestamp, format_timestamp_range_db

if(__name__) == "__main__":

    datetime_data = '2018-06-22'
    format1 = '%Y-%m-%d'
    
    date_object = format_timestamp(datetime_data, format1, True)
    
    print (date_object)

    datetime_data = "['14/06/2018', '22/06/2018']"
    
    format1 = '%d/%m/%Y'
        
    date_object = format_timestamp_range_db(datetime_data, format1, True)
    
    print (date_object)
