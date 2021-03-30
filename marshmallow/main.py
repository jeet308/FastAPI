from fastapi import FastAPI, UploadFile, Form, File, Request, status
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import schema as sch
import support as supp
from PIL import Image
import base64
import time
import os
import io
from datetime import datetime
import filetype
import asyncio
from schema import ImageSchema

app = FastAPI()
{}

time_stamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_out = supp.convert_error(exc.errors())
    return JSONResponse(
        {"data": None,
         "error": error_out,
         "status": "failed"},
          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        start_time = time.time()
        return await asyncio.wait_for(call_next(request), timeout=1)
    except asyncio.TimeoutError as e:
        process_time = time.time() - start_time
        return JSONResponse(
                {"data": None,
                 "error": {"type": "TimeoutError", "fields": None},
                 "status": "failed"},
                            status_code=status.HTTP_504_GATEWAY_TIMEOUT)


@app.post("/testapi/",status_code=200)
async def post_data(
    reference_id: str = Form(...,description="Reference id"),
    company_name: str = Form(...,description="Company name"),
    resize_width: Optional[int] = Form(None,description="Image resize width "),
    resize_height: Optional[int] = Form(None,description="Image resize height "),
    image_format: str = Form(...,description="Image file format "),
    quality_check: bool = Form(True,description="Image quality check"),
    image_file: UploadFile = File(...,description="Image file")):


    process_start_time = time.time()
    image_path = supp.save_file(image_file)

    file_extension = filetype.guess(image_path)
    
    try:
        input_data = sch.ImageSchema().load(
            {"reference_id": reference_id,
            "resize_width": resize_width,
            "resize_height": resize_height,
            "company_name": company_name,
            "quality_check": quality_check,
            "image_format": image_format,
            "image_file":image_file
            })
        
        image = Image.open(image_path)

        if resize_width != None:
            width_percent = (input_data['resize_width'] / float(image.size[0]))
            image_height = int((float(image.size[1]) * float(width_percent)))
            image = image.resize((input_data['resize_width'], image_height), Image.ANTIALIAS)
        else:
            height_percent = (input_data['resize_height'] / float(image.size[1]))
            image_width = int((float(image.size[0]) * float(height_percent)))
            image = image.resize((input_data['resize_height'], image_width), Image.ANTIALIAS)

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
        error_messages = supp.convert_error_string(e.__dict__['messages'])
        error = {"type": error_type, "fields": error_messages}
        data = None
        status = "falied"
        status_code = 400
    
            
    os.remove(image_path)
    res = JSONResponse({"data": data, "error": error, "status": status}, status_code=status_code)
    return res

