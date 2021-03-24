from marshmallow import Schema, fields, validate, ValidationError, validates
from pydantic import BaseModel

class ImageSchema(Schema):
    
    reference_id = fields.Str()
    resize_width = fields.Int()
    resize_height = fields.Int()
    company_name = fields.Str()
    image_format = fields.Str()
    quality_check = fields.Bool()
    

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

    @validates('resize_width')
    def resize_width_validate(cls, v):
        if v < 1 or v >= 1920 :
            raise ValidationError({
                "message": 'resize width must be 1 to 1920'})
        return v
    
    @validates('resize_height')
    def resize_height_validate(cls, v):
        if v < 1 or v >= 1920 :
            raise ValidationError({
                "message": 'resize height must be 1 to 1920'})
        return v

    @validates('image_format')
    def image_format_validate(cls, v):
        if v not in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp']:
            raise ValidationError({
                "message": f'{v} file is not supported'})
        return v

    
class Example(BaseModel):

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
