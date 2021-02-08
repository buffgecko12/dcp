import ast
import collections.abc
import json
import itertools

def convert_array_string_to_int_old(stringarray):
    try:
        return ast.literal_eval(stringarray)
    except:
        return stringarray # Return original array

def convert_array_string_to_int(stringarray):
    new_array = []

    # Clean up string
    stringarray_new = stringarray.replace("'", "").replace("]", "").replace("[", "").split(",")

    for item in stringarray_new:
        try:
            new_array.append(int(item))
        except:
            pass

    return new_array

def convert_string_array(mystring):
    result = []

    try:
        myarray_string = mystring.split(',') # Try to split string into an array
    except:
        myarray_string = list(map(int, mystring)) # Convert string array into into array

    for myvalue in myarray_string:
        try:
            myvalue = int(myvalue) # Check if value is integer
            result.append(myvalue) # Add value to new array
        except:
            pass # Don't append value

    return result

def subtract_arrays(original, current):
    result = []

    original_items = convert_string_array(original)
    current_items = convert_string_array(current)
    result = [myitem for myitem in original_items if myitem not in current_items]

    return result

def convert_form_binary_to_db(formfieldname):

    # Read signature scan file
    if formfieldname:
        myfile = formfieldname
        mydatafile = myfile.read()
    else:
        mydatafile = None

    return mydatafile

def to_array(value):
    if value:
        return value if (isinstance(value, collections.abc.Sequence) and (not isinstance(value, str))) else [value]
    else:
        return None

def get_matching_item(items, key, value):

    # Return if no items
    if not items:
        return None

    # Dictionary
    if isinstance(items[0], collections.abc.Mapping):
        return next((item for item in items if item.get(key) == value), None)

    # Objects
    else:
        return next((item for item in items if getattr(item, key, None) == value), None)

def generate_options(items, idfield, displayfield, removeduplicatesflag=True):

    seen = set()

    return [(str(getattr(myitem, idfield)), str(getattr(myitem, displayfield))) for myitem in items
            if (not (getattr(myitem, idfield) in seen or seen.add(getattr(myitem, idfield)))) and removeduplicatesflag
            ]

def to_json(mydict):
    return json.dumps(mydict) if mydict else None

def read_json(myjson, stringflag=True):
    if not stringflag:
        return json.load(myjson)
    else:
        return json.loads(myjson)

def convert_bytes_to_string(mybytes):
    return mybytes.decode('utf8').replace("'", "\"")

def convert_json_to_dict(myjson):
    return read_json(convert_bytes_to_string(myjson))

def multiply_lists(*args):
    return itertools.product(*args)

def group_items(items, groupbycolumn):
    keyfunc = lambda x: eval('x.' + groupbycolumn)
    data = sorted(items, key=keyfunc)
    groups = []

    for k, g in itertools.groupby(data, keyfunc):
        groups.append(list(g))
        
    return groups

def get_distinct_items(items, distinctfield):
    mylist = []
    seen = set() 

#     [seen.add(getattr(item, distinctfield)) or item for item in items if (item and (getattr(item, distinctfield) not in seen))]
    
    for item in items:
        myvalue = getattr(item, distinctfield)

        if myvalue not in seen:
            seen.add(myvalue)
            mylist.append(item)
    
    
    return mylist