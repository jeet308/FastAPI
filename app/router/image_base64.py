from fastapi import UploadFile, Form, File, APIRouter, Depends
from typing import Optional
from fastapi.responses import JSONResponse
from PIL import Image
import base64
import time
import io
from datetime import datetime
import uvicorn
from loguru import logger
from app import schema_py as sch
from app import utils, models, oauth2


router = APIRouter(
    tags=['Image To Base64']
)


@router.post("/image-to-base64", responses={200: {"model": utils.Example_200},
                                            422: {"model": utils.Example_422},
                                            504: {"model": utils.Example_504}})
async def image_converter(
        current_user: models.Client = Depends(oauth2.get_current_user),
        reference_id: str = Form(..., description="=6 character alphanumeric value"),
        company_name: str = Form(..., description="<30 character alphabetic value"),
        resize_width: Optional[int] = Form(None, description="image resize width"),
        resize_height: Optional[int] = Form(None, description="image resize height"),
        image_format: Optional[str] = Form(..., description="any of [jpg, jpeg, png, tiff, tif, webp]"),
        quality_check: bool = Form(True, description="image quality check"),
        image_file: UploadFile = File(..., description="image file")):

    logger.debug({"reference_id": reference_id,
                  "company_name": company_name,
                  "resize_width": resize_width,
                  "resize_height": resize_height,
                  "image_format": image_format,
                  "quality_check": quality_check })

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
        raise utils.ValidationException(e)

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





