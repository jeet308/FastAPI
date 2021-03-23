from fastapi import FastAPI, UploadFile, Form, File, Request, status
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import schema as sm
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
    error_out = convert_error_string(exc.errors())
    return JSONResponse({"data": None, "status": "failed", "error": error_out}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.post("/imagetest/",responses={200: {'model': sm.Example}})
async def post_data(
    reference_id: str = Form(...,description="Reference id"),
    company_name: str = Form(...,description="company name of the client "),
    resize_width: int = Form(...,description="image resize width "),
    resize_height: int = Form(...,description="image resizeheight "),
    image_format: str = Form(...,description="image file format "),
    quality_check: bool = Form(True,description="image quality check"),
    image_file: UploadFile = File(...,description="image file")):


    process_start_time = time.time()
    path = save_file(image_file)

    file_extension = os.path.splitext(image_file.filename)[-1]
    
    if file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp']:

        image_file_size = os.path.getsize(path)
        image = Image.open(path)

        try:
            input_data = sm.ImageSchema().load(
                {"reference_id": reference_id,
                 "resize_width": resize_width,
                 "resize_height": resize_height,
                 "company_name": company_name,
                 "quality_check": quality_check,
                 "image_format": image_format
                 })

            if (image_file_size < chunk_size):
                wpercent = (input_data['resize_width'] / float(image.size[0]))
                hsize = int((float(image.size[1]) * float(wpercent)))
                image = image.resize(
                    (input_data['resize_width'], hsize), Image.ANTIALIAS)
                buf = io.BytesIO()

                if file_extension in ['.jpg', '.jpeg']:
                    image.save(buf, format='JPEG')
                elif file_extension in ['.png']:
                    image.save(buf, format='PNG')
                elif file_extension in ['.tiff', '.tif']:
                    image.save(buf, format='TIFF')
                else:
                    image.save(buf, format='WEBP')
  
                base64_string = base64.b64encode(buf.getvalue()).decode()
                
            else:
                return JSONResponse(
                    {"data": None,
                     "error": {
                               "type": "input_error",
                               "field": "image_file",
                               "message": "file size mast be less than 10MB"
                              },
                     "status": "falied"
                    }, status_code=400)

            data = {
                "basestring": base64_string,
                "reference_id": input_data['reference_id'],
                "time_stamp": time_stamp,
                "processtime": (time.time() - process_start_time),
                   }
            status = "success"
            error = None
            status_code = 200
        except sm.ValidationError as e:
            error_type = e.__class__.__name__
            error_messages = convert_error_string(e.__dict__['messages'])
            error = {"type": error_type, "fields": error_messages}
            data = None
            status = "falied"
            status_code = 400
    else:
        return JSONResponse(
            {"data": None,
             "error": {
                       "type": "input_error",
                       "field": "image_file",
                       "message": "file formate not support"
                      },
             "status": "falied"
            }, status_code=400)
            
    os.remove(path)
    return JSONResponse({"data": data, "error": error, "status": status}, status_code=status_code)




def save_file(file):
    file_path = f"{file.filename}"
    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())
    return file_path

def convert_error_string(error):
    new_error = {}
    for key in error:
        new_error.update({key: {"message": error[key]}})
    return new_error
