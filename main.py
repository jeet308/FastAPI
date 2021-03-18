from fastapi import FastAPI, UploadFile, Form, File
from typing import Optional
from fastapi.responses import JSONResponse, PlainTextResponse
import schema as sm

from PIL import Image
import base64
import time
import os
from io import BytesIO
import io
from datetime import datetime

app = FastAPI()
{}

time_stamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
chunk_size = (10*1024)


@app.post("/imagetest/")
async def post_data(
    reference_id: str = Form(None),
    resize_width: str = Form('1028'),
    company_name: str = Form(None),
    image_format: str = Form(None),
    quality_check: str = Form('True'),
    image_file: UploadFile = File(...),
):

    process_start_time = time.time()
    #path = pt.pathfound(image_file.filename)
    #temp_file = os.path.join(path)
    image = read_imagefile(await image_file.read())

    image_file_size = len(image_file.filename)

    file_name,file_extension = os.path.splitext(image_file.filename)

    if file_extension in ['.jpg','.jpeg','.png']:
        
        #image_file_size = os.path.getsize(temp_file)

        try:
            input_data = sm.ImageSchema().load(
                {"reference_id": reference_id,
                "resize_width": resize_width,
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
                if file_extension in ['jpg','jpeg']:
                    image.save(buf, format='JPEG')
                else:
                    image.save(buf, format='PNG')
                base64_string = base64.b64encode(buf.getvalue()).decode()

            else:
                return JSONResponse(
                {"data": None,
                "error": {
                    "type":"input_error",
                    "field":"image_file",
                    "message":"file size mast be less than 10MB"
                        },
                "status":"falied"
                },status_code=400)

            data = {
                "basestring": base64_string,
                "reference_id": input_data['reference_id'],
                "time_stamp": time_stamp,
                "processtime": (time.time() - process_start_time),
                "size":image_file_size
            }
            status = "success"
            error = None
            status_code = 200
        except sm.ValidationError as e:
            data = None
            status = "falied"
            error = str(e)
            status_code = 400

    else:
                return JSONResponse(
                {"data": None,
                "error": {
                    "type":"input_error",
                    "field":"image_file",
                    "message":"file formate not support"
                        },
                "status":"falied"
                },status_code=400)   

    return JSONResponse({"data": data, "error": error, status: status}, status_code=status_code)



def read_imagefile(file):
    image = Image.open(BytesIO(file))
    return image
