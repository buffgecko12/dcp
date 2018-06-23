from django.db import connection
from collections import namedtuple

# TO-DO
# Check for valid connection (DB is up, valid credential)
# Error-handling for queries, timeout
# Handle non-ASCII characters (Python default encoding is ASCII)

# Return data as a RawQuerySet object (list of objects)
def get_data(myobjects, sp_signature, params):
    # IMPORTANT: Model field names must match column names in DB
    resultset = myobjects.raw('select * from ' + sp_signature, params)

    # Check if resultset has any rows
    try:
        test = resultset[0] 
    except IndexError:
        return myobjects.none() # return empty queryset ("not myobjects.none() evaluates to True)
#         return None
#         raise myobjects.model._meta.model.DoesNotExist

    # Return result set
    return resultset

# Return data as a single model object
def get_data_pk(myobjects, sp_signature, params):
    resultset = get_data(myobjects, sp_signature, params)
    
    # If there is a result set, return the first instance
    if(resultset):
        return resultset[0] 

# Return data as a QuerySet object (first column in resultset must be the PK for the model
def get_data_qs(self, sp_signature, params, pk_fieldname = None):
    cursor = connection.cursor()
    try:
        # Use default PK if not provided
        if(not pk_fieldname):
            pk_fieldname = self.model._meta.pk.name
            
        # Create "IN" filter
        myfilter = pk_fieldname + '__in' 

        # Execute query and apply filter to convert to QuerySet        
        cursor.execute("select * from " + sp_signature, params)
        return self.filter(**{ myfilter: (x[0] for x in cursor) }) # TO-DO: This may need looking at due to Python 3 conversion

    finally:
        cursor.close()

# Return data as a non-objectified result set (list of rows)
def get_data_raw(sp_name, params):
    with connection.cursor() as cursor:        
        cursor.callproc(sp_name, params)
        return_data = namedtuplefetchall(cursor) # Format output as standard row result set (list of tuples)
        cursor.close()
         
    return return_data

def save_data(sp_name, params):
    with connection.cursor() as cursor:        
        cursor.callproc(sp_name, params)
        return_data = cursor.fetchone() # Store any output
        cursor.close()
        
    return return_data

# TO-DO: Write new delete_data function
def delete_data(sp_name, params):
    return save_data(sp_name, params)

# Return all rows from a cursor as named tuples (i.e. rows with field names)
def namedtuplefetchall(cursor):
    columns = [col[0] for col in cursor.description]
    nt_result = namedtuple('Result', columns)

    return [
        nt_result(*row) 
        for row in cursor.fetchall()
    ]