from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
import utils as sup
import os
import filetype
from PIL import Image
import numpy as np
from loguru import logger

chunk_size = (5*1024*1024)

class ImageSchema(Schema):
    reference_id = fields.Str()
    resize_width = fields.Int(missing=None)
    resize_height = fields.Int(missing=None)
    company_name = fields.Str()
    image_format = fields.Str(validate=validate.OneOf(['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']))
    quality_check = fields.Bool()
    image_file = fields.Field()
    image_type = fields.Str()

    @validates_schema
    def reference_id_validate(cls, data, **kwargs):
        if not data['reference_id'].isalnum():
            raise ValidationError("reference_id must be alphanumeric",'reference_id')
        if len(data['reference_id']) != 6:
            raise ValidationError("reference_id length must be 6",'reference_id')
        return data

    @validates_schema
    def company_name_validate(cls, data, **kwargs):
        if not data['company_name'].isalpha():
            raise ValidationError("company name must be alphabetic only",'company_name')
        if len(data['company_name']) < 0 and len(data['company_name']) < 30:
            raise ValidationError(
                "company name length must be 1 to 30 characters",'company_name')
        return data

    @validates_schema
    def check_height_width(cls, data, **kwargs):
        w = data['resize_width']
        h = data['resize_height']

        if w is not None and h is None:
            if (w < 1 or w >= 1920):
                raise ValidationError('resize_width must be 1 to 1920', 'resize_width')
        elif h is not None and w is None:
            if (h < 1 or h >= 1920):
                raise ValidationError('resize_height must be 1 to 1920', 'resize_height')
        else:
            raise ValidationError('Please use any one of resize_height or resize_width', 'common')
        return data

    @validates_schema
    def image_file_validate(cls, data, **kwargs):
        try:
            image_file = data["image_file"]
            image_path = sup.save_file(image_file)
        except:
            raise ValidationError("field required", "image_file")

        file_type = filetype.guess(image_path)
        image_file_size = os.path.getsize(image_path)

        if file_type != None:
            file_extension = file_type.extension
            if file_extension not in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:
                raise ValidationError('file format is not supported', "image_file")
        else:
            raise ValidationError('file is not supported', "image_file")
        if chunk_size < image_file_size:
            raise ValidationError("file size must be less than 5 MB", "image_file")

        rgba_image = Image.open(image_path)
        rgb_image = rgba_image.convert('RGB')
        width, height = rgb_image.size
        if width > 2000:
            raise ValidationError("image width must be less than 2000 pixel", "image_file")
        if height > 2000:
            raise ValidationError("image height must be less than 2000 pixel", "image_file")

        np_img = np.array(rgb_image)
        data["image_file"] = np_img
        data["image_type"] = file_extension

        logger.debug(f"file extension: {file_extension}")

        return data
