from fastapi import FastAPI, UploadFile, Form, File, Request, status
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import schema as sch
from PIL import Image
import base64
import time
import os
import io
from datetime import datetime

app = FastAPI()
{}

time_stamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
chunk_size = (10*1024*1024)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_out = convert_error(exc.errors())
    return JSONResponse(
        {"data": None,
         "error": error_out,
         "status": "failed"},
          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.post("/testapi/",responses={200: {'model': sch.Example}})
async def post_data(
    reference_id: str = Form(...,description="Reference id"),
    company_name: str = Form(...,description="Company name"),
    resize_width: int = Form(...,description="Image resize width "),
    resize_height: int = Form(...,description="Image resize height "),
    image_format: str = Form(...,description="Image file format "),
    quality_check: bool = Form(True,description="Image quality check"),
    image_file: UploadFile = File(...,description="Image file")):


    process_start_time = time.time()
    image_path = save_file(image_file)

    file_extension = image_file.filename.split('.')[-1]
    
    if file_extension in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:

        image_file_size = os.path.getsize(image_path)
        image = Image.open(image_path)

        try:
            input_data = sch.ImageSchema().load(
                {"reference_id": reference_id,
                 "resize_width": resize_width,
                 "resize_height": resize_height,
                 "company_name": company_name,
                 "quality_check": quality_check,
                 "image_format": image_format
                 })

            if (image_file_size < chunk_size):
                width_percent = (input_data['resize_width'] / float(image.size[0]))
                image_height = int((float(image.size[1]) * float(width_percent)))
                image = image.resize(
                    (input_data['resize_width'], image_height), Image.ANTIALIAS)
                buf = io.BytesIO()

                if file_extension in ['jpg', 'jpeg']:
                    image.save(buf, format='JPEG')
                elif file_extension in ['png']:
                    image.save(buf, format='PNG')
                elif file_extension in ['tiff', 'tif']:
                    image.save(buf, format='TIFF')
                else:
                    image.save(buf, format='WEBP')
  
                base64_string = base64.b64encode(buf.getvalue()).decode()
                
            else:
                os.remove(image_path)
                return JSONResponse(
                    {"data": None,
                     "error": {
                               "type": "ValidationError",
                               "field": "image_file",
                               "message": "file size must be less than 10MB"
                              },
                     "status": "failed"
                    }, status_code=400)

            data = {
                "base64_string": base64_string,
                "reference_id": input_data['reference_id'],
                "time_stamp": time_stamp,
                "process_time": (time.time() - process_start_time),
                   }
            status = "success"
            error = None
            status_code = 200
        except sch.ValidationError as e:
            error_type = e.__class__.__name__
            error_messages = convert_error_string(e.__dict__['messages'])
            error = {"type": error_type, "fields": error_messages}
            data = None
            status = "falied"
            status_code = 400
    else:
        os.remove(image_path)
        return JSONResponse(
            {"data": None,
             "error": {
                       "type": "ValidationError",
                       "field": "image_file",
                       "message": f"{file_extension} file not support"
                      },
             "status": "failed"
            }, status_code=400)
            
    os.remove(image_path)
    return JSONResponse({"data": data, "error": error, "status": status}, status_code=status_code)


def save_file(file):
    file_path = f"{file.filename}"
    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())
    return file_path

def convert_error_string(error):
    new_error = []
    for key in error:
        new_error.append({key: error[key]})
    return new_error

def convert_error(exc):
    error_fields = []
    for data in exc:
        temp_field = data['loc'][1] if len(data['loc']) > 1 else data['loc'][0]
        temp_mes = data['msg']
        error_fields.append({temp_field: {'meesage': temp_mes}})
    return {"type": "ValidationError", "fields": error_fields}
