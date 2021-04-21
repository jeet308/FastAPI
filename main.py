from fastapi import FastAPI, UploadFile, Form, File, Request, status
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
# import schema_mar as sch
import schema_py as sch
import utils
from PIL import Image
import base64
import time
import io
from datetime import datetime
import asyncio
import os
import log
import uuid
import uvicorn

app = FastAPI()

logger = log._init_logger()

@app.middleware("http")
async def request_middleware(request, call_next):
    end_point = request.url.path
    request_id = str(uuid.uuid4())
    with logger.contextualize(request_id=request_id,end_point=end_point):
        logger.debug('--------------start--------------') 

        try:
            return await call_next(request)
        except Exception as ex:
            print(ex)
            logger.error(f"Request failed: {ex}")
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content={"error": {"type": "UnknownError",
                                                   "message": "Unknown error found. Try with different image.",
                                                   "fields": None}, "status": "failed"})
        finally:
            logger.debug('---------------end---------------')


class ValidationException(Exception):
    def __init__(self, exception):
        self.errors_out = utils.convert_error_pydantic(exception.errors()) # use with pydantic validation
        # self.errors_out = utils.convert_error_marshmallow(exception.__dict__['messages']) # use with marshmallow validation

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={"error": exc.errors_out,"status": "failed"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_out = utils.convert_error_pydantic(exc.errors())
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={"error": error_out,"status": "failed"})

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=1000)
    except asyncio.TimeoutError:
        return JSONResponse(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content = {"error": {"type": "TimeoutError", "message": "API timed out.", "fields": None},"status": "failed"})


@app.post("/test", responses={200: {"model": utils.Example_200},
                              422: {"model": utils.Example_422},
                              504: {"model": utils.Example_504}})

async def post_data(
        reference_id: str = Form(..., description="=6 character alphanumeric value"),
        company_name: str = Form(..., description="<30 character alphabetic value"),
        resize_width: Optional[int] = Form(None, description="image resize width"),
        resize_height: Optional[int] = Form(None, description="image resize height"),
        image_format: Optional[str] = Form(..., description="any of [jpg, jpeg, png, tiff, tif, webp]"),
        quality_check: bool = Form(True, description="image quality check"),
        image_file: UploadFile = File(..., description="image file")):

    logger.debug({"reference_id":reference_id,
                 "company_name":company_name,
                 "resize_width":resize_width,
                 "resize_height":resize_height,
                 "image_format":image_format,
                 "quality_check":quality_check
                 })

    process_start_time = time.time()

    try:
        # remove this to use marshmallow validation
        # input_data_dict = sch.ImageSchema().load(
        #     {"reference_id": reference_id,
        #      "resize_width": resize_width,
        #      "resize_height": resize_height,
        #      "company_name": company_name,
        #      "quality_check": quality_check,
        #      "image_format": image_format,
        #      "image_file": image_file
        #      })
        #
        # input_data = utils.dict2obj(input_data_dict)

        # remove comment to use pydnatic validation

        image_path = await utils.save_file_aiof(image_file)

        input_data = sch.ImageSchema(
            reference_id=reference_id,
            resize_width=resize_width,
            resize_height=resize_height,
            company_name=company_name,
            quality_check=quality_check,
            image_format=image_format,
            image_file=image_path
        )

    except sch.ValidationError as e:
        raise ValidationException(e)

    image = Image.fromarray(input_data.image_file)

    if resize_width != None:
        width_percent = (input_data.resize_width / float(image.size[0]))
        image_height = int((float(image.size[1]) * float(width_percent)))
        image = image.resize((input_data.resize_width, image_height), Image.ANTIALIAS)
    else:
        height_percent = (input_data.resize_height / float(image.size[1]))
        image_width = int((float(image.size[0]) * float(height_percent)))
        image = image.resize((input_data.resize_height, image_width), Image.ANTIALIAS)

    buf = io.BytesIO()

    image.save(buf, format='JPEG')
    base64_string = base64.b64encode(buf.getvalue()).decode()
    time_stamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    data = {
        "base64_string": base64_string,
        "reference_id": input_data.reference_id,
        "time_stamp": time_stamp,
        "process_time": (time.time() - process_start_time),
    }

    return JSONResponse({"data": data, "status": "success"}, status_code=200)


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8001)
