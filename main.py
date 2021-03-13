from fastapi import FastAPI, UploadFile, Form, File
from typing import Optional
from fastapi.responses import JSONResponse, PlainTextResponse
import schema as sm

from PIL import Image
import base64
import time
import os
import io
import datetime

app = FastAPI()
{}

currentdatetime = datetime.datetime.now()
chunk_size = (10*1024*1024)


@app.post("/imagetest/")
def post_data(
    reference_id: str = Form(None),
    resize_width: str = Form('1028'),
    company_name: str = Form(None),
    image_format: str = Form(None),
    quality_check: str = Form('True'),
    image_file: UploadFile = File(...)
):

    process_start_time = time.time()
    path = os.getcwd()
    temp_file = os.path.join(path, image_file.filename)

    image = Image.open(temp_file)
    #image_format = image.format

    image_file_size = os.path.getsize(temp_file)

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
            image.save(buf, format='JPEG')
            base64_string = base64.b64encode(buf.getvalue()).decode()

        else:
            return JSONResponse(status_code=404, content={"message": "File size mast be lessthan 10 MB"})

        data = {
            "basestring": base64_string,
            "reference_id": input_data['reference_id'],
            "time_stamp": currentdatetime,
            "processtime": (time.time() - process_start_time),
        }
        status = "success"
        error = None
        status_code = 200
    except sm.ValidationError as e:
        data = None
        status = "falied"
        error = str(e)
        status_code = 400

    return JSONResponse({"data": data, "error": error, status: status}, status_code=status_code)
