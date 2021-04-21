from pydantic import BaseModel, ValidationError, validator, root_validator
from fastapi import UploadFile
from typing import Optional
import utils as sup
import os
import filetype
from PIL import Image
import numpy as np
from loguru import logger


chunk_size = (5*1024*1024)

class ImageSchema(BaseModel):
    reference_id : str
    resize_width : Optional[int] = None
    resize_height : Optional[int] = None
    company_name : str
    image_format : str
    quality_check : bool
    # image_file : UploadFile = None
    image_file : str

    @validator('reference_id')
    def reference_id_validate(cls, v):
        if not v.isalnum():
            raise ValueError("reference_id must be alphanumeric")
        if len(v) != 6:
            raise ValueError("reference_id length must be 6")
        return v

    @validator('company_name')
    def company_name_validate(cls, v):
        if not v.isalpha():
            raise ValueError("company_name must be alphabetic only")
        if len(v) < 0 and len(v) < 30:
            raise ValueError("company_name length must between 1 to 30 characters")
        return v

    @root_validator()
    def check_height_width(cls, values):
        w = values.get('resize_width')
        h = values.get('resize_height')

        if w is not None and h is None:
            if (w < 1 or w >= 1920):
                raise ValueError('resize_width must be 1 to 1920')
        elif h is not None and w is None:
            if (h < 1 or h >= 1920):
                raise ValueError('resize_height must be 1 to 1920')
        else:
            raise ValueError('Please use any one of resize_height or resize_width')

        return values

    @validator('image_file')
    def image_file_validate(cls, image_path):
        # try:
        #     image_path = sup.save_file(v)
        # except:
        #     raise ValueError("field required")

        file_type = filetype.guess(image_path)
        image_file_size = os.path.getsize(image_path)

        if file_type != None:
            file_extension = file_type.extension
            if file_extension not in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:
                raise ValidationError('file format is not supported', "image_file")
        else:
            raise ValueError('file is not supported')
        if chunk_size < image_file_size:
            raise ValueError("file size must be less than 5 MB")

        image = Image.open(image_path)
        width, height = image.size
        if width > 5000:
            raise ValueError("image width must be less than 5000 pixel")
        if height > 5000:
            raise ValueError("image height must be less than 5000 pixel")

        np_img = np.array(image)

        logger.debug(f"file extension: {file_extension}")

        os.remove(image_path)
        return np_img
