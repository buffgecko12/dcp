import ast

def convert_array_string_to_int(stringarray):
    try:
        return ast.literal_eval(stringarray)
    except:
        return stringarray # Return original array