import os    

def get_file_info(file_path):
    file_data = open(file_path, 'rb').read()
    file_size = os.path.getsize(file_path)
    file_name= get_file_name_info(file_path)['file_name']
    file_extension = get_file_name_info(file_path)['file_extension']

    return {
        "file_name": file_name,
        "file_extension": file_extension,
        "file_size": file_size,
        "file_data": file_data,
        }
    
def get_file_name_info(file_path):
    file_name, file_extension = os.path.splitext(os.path.split(file_path)[1])

    return {
        "file_name": file_name,
        "file_extension": file_extension,
        }