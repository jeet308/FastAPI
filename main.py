from fastapi import FastAPI, File, UploadFile, status,Response, Query,Path
from pydantic import BaseModel,Field
from typing import Optional
from fastapi.responses import JSONResponse
import shutil
import base64
import os
import io
from PIL import Image
import datetime
import time

app = FastAPI()

ct = datetime.datetime.now() 


@app.post("/uploadfile/",status_code=200)
async def create_upload_file(
    response: Response,
    company_name:str = Query (...,regex="([a-zA-Z])\D*([a-zA-Z])$"),
    img_width:int = Query(1024,ge=1,le=1920),
    image_quality_check:bool=True,
    image_formate:Optional[str] = Query (None,title="jpeg, png, tiff, webp"),
    ref_id:str = Query (...,regex="^[a-zA-Z0-9]*_?[a-zA-Z0-9]*$",max_length=6),
    file: UploadFile = File(...),
    ):

    start_time = time.time()
    path = os.getcwd()
    temp_file = os.path.join(path,file.filename)

    img = Image.open(temp_file)
    img_format = img.format

    img_file_size = os.path.getsize(temp_file)

    if (img_file_size<(10*1024*1024)):
        if (img_format == "JPEG") | (img_format == "PNG"):
            wpercent = (img_width / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent))) 
            img = img.resize((img_width, hsize), Image.ANTIALIAS)
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            base_img = base64.b64encode(buf.getvalue()).decode()
            response.status_code = status.HTTP_201_CREATED
            return {"Base64_string":base_img,
            "ref_id":ref_id,
            "timestamp":ct,
            "time":(time.time() - start_time),"status": "Image base string created"}

        else:
            return JSONResponse(status_code=404, content={"message": "File formate not support"})

    else:
        return JSONResponse(status_code=404, content={"message": "File size mast be lessthan 10 MB"})








