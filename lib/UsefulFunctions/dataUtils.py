import ast

def convert_array_string_to_int(stringarray):
    try:
        return ast.literal_eval(stringarray)
    except:
        return stringarray # Return original array
    
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

