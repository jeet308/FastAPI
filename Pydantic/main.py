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


def read_imagefile(file):
    image = Image.open(BytesIO(file))
    return image


def convert_error(exc):
    error = {}
    error_fields = []
    error_types = []
    for data in exc:
        temp_field = data['loc'][1] if len(data['loc']) > 1 else data['loc'][0]
        temp_mes = data['msg']
        temp_type = data['type']
        error_fields.append({temp_field: {'meesage': temp_mes}})
        error_types.append(temp_type)
    return {"type": "ValidationError", "fields": error_fields}


class ImageModel(BaseModel):

    reference_id: str
    resize_width: int
    resize_height: int
    image_format: str
    company_name: str
    quality_check: bool

    @validator('reference_id')
    def reference_id_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('reference_id must be alphanumeric')
        if len(v) != 6:
            raise ValueError('reference_id length must be 6')
        return v
        
    @validator('company_name')
    def companyname_length(cls, v):
        if len(v)<0 and len(v)<30 :
            raise ValueError('company name btween 0 to 30')
        return v
    
    @validator('resize_width')
    def resize_width_check(cls, v):
        if v < 100 or v >= 1920 :
            raise ValueError('resize width mast be 1 to 1920')
        return v
    
    @validator('resize_height')
    def resize_height_check(cls, v):
        if v < 100 or v >= 1920 :
            raise ValueError('resize height mast be 1 to 1920')
        return v

    @validator('image_format')
    def image_must_contain(cls, v):
        if v not in ['jpg', 'jpeg', 'png']:
            raise ValueError(f'{v} image_format is not supported')
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
    return JSONResponse({"data": None, "status": "failed", "error": error_out}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post(path="/test",responses={200: {'model': ImageModel}})
async def get_response(reference_id: str = Form(...,description="Reference id"),
                       company_name: str = Form(...,description="company name of the client "),
                       resize_width: int = Form(...,description="image resize width "),
                       resize_height: int = Form(...,description="image resizeheight "),
                       image_format: str = Form(...,description="image file format "),
                       quality_check: bool = Form(True,description="image quality check"),
                       image_file: UploadFile = File(...,description="image file"),
                       ):

    process_start_time = time.time()
    file_extension = os.path.splitext(image_file.filename)[-1]

    if file_extension in ['.jpg', '.jpeg', '.png']:

        image = read_imagefile(await image_file.read())

        image_file_size = len(image.fp.read())

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
                wpercent = (resize_width / float(image.size[0]))
                hsize = int((float(image.size[1]) * float(wpercent)))
                image = image.resize(
                    (resize_width, hsize), Image.ANTIALIAS)
                buf = io.BytesIO()
                if file_extension in ['jpg', 'jpeg']:
                    image.save(buf, format='JPEG')
                else:
                    image.save(buf, format='PNG')
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
                "reference_id": reference_id,
                "time_stamp": time_stamp,
                "processtime": (time.time() - process_start_time)
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
        return JSONResponse(
            {"data": None,
             "error": {
                 "type": "input_error",
                 "field": "image_file",
                 "message": "file formate not support"
             },
                "status": "falied"
             }, status_code=400)

    return JSONResponse({"data": data, "error": error, "status": status}, status_code=status_code)
