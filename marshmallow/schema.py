from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from pydantic import BaseModel
import support as sup
import os
import filetype


chunk_size = (10*1024*1024)

class ImageSchema(Schema):

    reference_id = fields.Str()
    resize_width = fields.Int(missing=None)
    resize_height = fields.Int(missing=None)
    company_name = fields.Str()
    image_format = fields.Str()
    quality_check = fields.Bool()
    image_file = fields.Field()


    @validates('reference_id')
    def reference_id_validate(cls, v):
        if not v.isalnum():
            raise ValidationError({
                "message": "reference id must be alphanumeric"})
        if len(v) != 6:
            raise ValidationError({
                "message": "reference id length must be 6"})
        return v

    @validates('company_name')
    def company_name_validate(cls, v):
        if not v.isalpha():
            raise ValidationError({
                "message": "company name must be alphabetic only"})
        if len(v)<0 and len(v)<30 :
            raise ValidationError({
                "message": "company name length must be 1 to 30 characters"})
        return v

    @validates('image_format')
    def image_format_validate(cls, v):
        if v not in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:
            raise ValidationError({
                "message": f'{v} file is not supported'})
        return v

    @validates_schema
    def check_height_width(cls, data, **kwargs):
        if data['resize_width'] is not None and data['resize_height'] is None:
            if (data['resize_width'] < 1 or data['resize_width'] >= 1920):
                raise ValidationError({"message": 'resize width must be 1 to 1920'})
        elif data['resize_height'] is not None and data['resize_width'] is None:
            if (data['resize_height'] < 1 or data['resize_height'] >= 1920) :
                raise ValidationError({"message": 'resize height must be 1 to 1920'})
        else:
            raise ValidationError({
                "message": 'Please use any one of resize_height or resize_width'})
        return data

    @validates('image_file')
    def reference_id_validate(cls, v):

        image_path=v.filename
        file_extension = filetype.guess(image_path)
        image_file_size = os.path.getsize(image_path)
        
        if file_extension != None:
            extension = file_extension.extension
            if extension not in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:
                raise ValidationError({"message":'file is not supported'}) 
        else:
            raise ValidationError({"message":' file is not supported'}) 

        if chunk_size < image_file_size:
            raise ValidationError({
                "message": f"file size must be less than 10MB"})
        
        width, height = sup.pixel_size(image_path)
        if width > 2000:
            raise ValidationError({
                "message": f"image width must be less than 2000 pixel"})
        if height > 2000:
            raise ValidationError({
                "message": f"image height must be less than 2000 pixel"})       
        return v


class Example_422(BaseModel):

    class Config:
        schema_extra = {
            "example": {
                "reference_id":  "abcd12",
                "resize_width":  500,
                "resize_height": 200,
                "company_name":  "frslabs",
                "image_format":  "png",
                "quality_check":  False,
            }
        }

class Example_400(BaseModel):

    class Config:
        schema_extra = {
            "example": {
                "reference_id":  "abcd12",
                "resize_width":  500,
                "resize_height": 200,
                "company_name":  "frslabs",
                "image_format":  "png",
                "quality_check":  False,
            }
        }
    

class Example_200(BaseModel):

    class Config:
        schema_extra = {
            "example": {
                "We received the request"
            }
        }
    

        
