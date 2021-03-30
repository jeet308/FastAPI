
def save_file(file):
    file_path = f"{file.filename}"
    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())
    return file_path

def convert_error_string(error):
    new_error = []
    for key in error:
        message = ''.join(error[key])
        new_error.append({key: {"message":message}})
    return new_error

def convert_error(exc):
    error_fields = []
    for data in exc:
        temp_field = data['loc'][1] if len(data['loc']) > 1 else data['loc'][0]
        temp_mes = data['msg']
        error_fields.append({temp_field: {'meesage': temp_mes}})
    return {"type": "ValidationError", "fields": error_fields}

