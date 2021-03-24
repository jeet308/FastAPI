from fastapi import FastAPI, File, UploadFile, status, Response, Query, Path, Form
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from pydantic import BaseModel, ValidationError, validator
import json

from PIL import Image
import io
from io import BytesIO
import os
import time
from datetime import datetime
import base64


app = FastAPI()

time_stamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
chunk_size = (10*1024*1024)

class ImageModel(BaseModel):

    reference_id: str
    resize_width: int
    resize_height: int
    image_format: str
    company_name: str
    quality_check: bool

    @validator('reference_id')
    def reference_id_validate(cls, v):
        if not v.isalnum():
            raise ValueError('reference id must be alphanumeric')
        if len(v) != 6:
            raise ValueError('reference id length must be 6')
        return v
        
    @validator('company_name')
    def company_name_validate(cls, v):
        if not v.isalpha():
            raise ValueError("company name must be alphabetic only")
        if len(v)<0 and len(v)<30 :
            raise ValueError('company name length must be 1 to 30 characters')
        return v
    
    @validator('resize_width')
    def resize_width_validate(cls, v):
        if v < 1 or v >= 1920 :
            raise ValueError('resize width must be 1 to 1920')
        return v
    
    @validator('resize_height')
    def resize_height_validate(cls, v):
        if v < 1 or v >= 1920 :
            raise ValueError('resize height must be 1 to 1920')
        return v

    @validator('image_format')
    def image_format_validate(cls, v):
        if v not in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:
            raise ValueError(f'{v} file is not supported')
        return v

    class Config:
        schema_extra = {
            "example": {
                "reference_id":  "abcd12",
                "resize_width":  1250,
                "resize_height": 500,
                "company_name":  "frslabs",
                "image_format":  "png",
                "quality_check": True,
            }
        }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_out = convert_error(exc.errors())
    return JSONResponse({"data": None,
                         "status": "failed",
                         "error": error_out},
                          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post(path="/test",responses={200: {'model': ImageModel}})
async def get_response(
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
            input_data = ImageModel(
                reference_id=reference_id,
                company_name=company_name,
                resize_width=resize_width,
                resize_height=resize_height,
                image_format=image_format,
                quality_check=quality_check
            )

            if (image_file_size < chunk_size):
                width_percent = (resize_width / float(image.size[0]))
                image_height = int((float(image.size[1]) * float(width_percent)))
                image = image.resize(
                    (resize_width, image_height), Image.ANTIALIAS)
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
                "base_string": base64_string,
                "reference_id": reference_id,
                "time_stamp": time_stamp,
                "process_time": (time.time() - process_start_time)
                  }
            status = "success"
            status_code = 200
            error = None
        except ValueError as e:
            print(e)
            data = None
            status_code = 422
            error = convert_error(e.errors())
            status = "failed"

    else:
        os.remove(image_path)
        return JSONResponse(
            {"data": None,
             "error": {
                 "type": "ValidationError",
                 "field": "image_file",
                 "message": f"{file_extension} file not support"
             },
                "status": "falied"
             }, status_code=400)

    os.remove(image_path)
    return JSONResponse({"data": data, "error": error, "status": status}, status_code=status_code)



def save_file(file):
    file_path = f"{file.filename}"
    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())
    return file_path

def convert_error(exc):
    error_fields = []
    for data in exc:
        temp_field = data['loc'][1] if len(data['loc']) > 1 else data['loc'][0]
        temp_mes = data['msg']
        error_fields.append({temp_field: {'meesage': temp_mes}})
    return {"type": "ValidationError", "fields": error_fields}
