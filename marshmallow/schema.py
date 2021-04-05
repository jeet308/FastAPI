from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from pydantic import BaseModel
import support as sup
import os
import filetype
from PIL import Image
import numpy as np
from helper import GetLogger

chunk_size = (10*1024*1024)

logg = GetLogger()
log = logg.get_logger()

class ImageSchema(Schema):
    reference_id = fields.Str()
    resize_width = fields.Int(missing=None)
    resize_height = fields.Int(missing=None)
    company_name = fields.Str()
    image_format = fields.Str()
    quality_check = fields.Bool()
    image_file = fields.Str()

    @validates('reference_id')
    def reference_id_validate(cls, v):
        if not v.isalnum():
            raise ValidationError("reference id must be alphanumeric")
        if len(v) != 6:
            raise ValidationError("reference id length must be 6")
        return v

    @validates('company_name')
    def company_name_validate(cls, v):
        if not v.isalpha():
            raise ValidationError("company name must be alphabetic only")
        if len(v) < 0 and len(v) < 30:
            raise ValidationError(
                "company name length must be 1 to 30 characters")
        return v

    @validates('image_format')
    def image_format_validate(cls, v):
        if v not in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:
            raise ValidationError(f'{v} file is not supported')
        return v

    @validates_schema
    def check_height_width(cls, data, **kwargs):
        if data['resize_width'] is not None and data['resize_height'] is None:
            if (data['resize_width'] < 1 or data['resize_width'] >= 1920):
                raise ValidationError('resize width must be 1 to 1920','resize_width')
        elif data['resize_height'] is not None and data['resize_width'] is None:
            if (data['resize_height'] < 1 or data['resize_height'] >= 1920):
                raise ValidationError('resize height must be 1 to 1920','resize_height')
        else:
            raise ValidationError(
                'Please use any one of resize_height or resize_width','common')
        return data

    @validates_schema
    def image_file_validate(cls, data, **kwargs):
        image_path = data["image_file"]
        file_extension = filetype.guess(image_path)
        image_file_size = os.path.getsize(image_path)
        image_type = file_extension.mime

        if file_extension != None:
            extension = file_extension.extension
            if extension not in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:
                raise ValidationError('file is not supported',"image_file")
        else:
            raise ValidationError('file is not supported',"image_file")
        if chunk_size < image_file_size:
            raise ValidationError(f"file size must be less than 10MB","image_file")

        image = Image.open(image_path)
        width, height = image.size
        if width > 2000:
            raise ValidationError(f"image width must be less than 2000 pixel","image_file")
        if height > 2000:
            raise ValidationError(f"image height must be less than 2000 pixel","image_file")

        np_img = np.array(image)
        data["image_file"] = np_img

        log.debug(image_type)

        return data


class Example_200(BaseModel):

    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "base64_string": "UklGRrQBAABXRUJQVlA4WAoAAAAQAAAAMQAAGwAAQUxQSCIAAAABF7D9EREBo7aRJM21i3AMcoN2nxH9jwuA+VVVVe9PvACYVlA4IGwBAAAQBwCdASoyABwAPm02l0gkIyIhJApIgA2JZz5owtVXjtBBBHiINLjBN5jWSk49bfuJCqbYWZ7XW1WgnN6Clg6KAAD+2+qf9rnRIkhj5SmyCEU/2vDv4WLuPCtPZ0z85RPS9UT/DdgDiJb6ct90KwpiwVQimg8xQS/VYxIvE9M8po5eIS3LUblYCy8DzHHoQfeplwBKR5JWqHnspQID7fH2iHg8S3aXsGev4FcljKc9mrRQfMAszhNlGzyPnHoMAxDvX8ch1K+4YcuHbl+ST6UyvgPQBvc+Xrptb7SSE3y4zr7bfk38PYavkTlPun5O4+HfJ5KPZ+Eo9Hevw7jNfWN7F7C9C6FRCPRynuyu76+TGhZBN/7Te4OYrgYAaGqqr4s0jDFxgY9RRSZKF47gokXqE8dQsPaAAMgMfW0FPf/pIp9gv1k9fhLEXk3p4lpLZnsESgWs703hpIm9x99VsTEkMFwZOunZvlN+QAAA",
                    "reference_id": "abcd12",
                    "time_stamp": "2021-03-31T14:26:13",
                    "process_time": 0.08904647827148438
                },
                "error": "null",
                "status": "success",
            }
        }


class Example_422(BaseModel):

    class Config:
        schema_extra = {
            "example": {
                "data": "null",
                "error": {
                    "type": "ValidationError",
                    "fields": [
                        {
                            "reference_id": {
                                "message": "reference id length must be 6"
                            }
                        }
                    ]
                },
                "status": "falied",
            }
        }
