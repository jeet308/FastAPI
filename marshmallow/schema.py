from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from datetime import datetime
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
                "message": "reference_id must be alphanumeric"})
        if len(v) != 6:
            raise ValidationError({
                "message": "reference_id length must be 6"})
        return v

    @validates('company_name')
    def companyname_length(cls, v):
        if len(v)<0 and len(v)<30 :
            raise ValidationError({
                "message": "company name btween 0 to 30"})
        return v

    @validates('resize_width')
    def resize_width_check(cls, v):
        if v < 100 or v >= 1920 :
            raise ValidationError({
                "message": 'resize width mast be 1 to 1920'})
        return v
    
    @validates('resize_height')
    def resize_height_check(cls, v):
        if v < 100 or v >= 1920 :
            raise ValidationError({
                "message": 'resize height mast be 1 to 1920'})
        return v

    @validates('image_format')
    def image_must_contain(cls, v):
        if v not in ['jpg', 'jpeg', 'png']:
            raise ValidationError({
                "message": f'{v} image_format is not supported'})
        return v

    
class Example(BaseModel):

    class Config:
        schema_extra = {
            "example": {
                "reference_id":  "abcd12",
                "resize_width":  1250,
                "resize_height": 500,
                "company_name":  "frslabs",
                "image_format":  "png",
                "quality_check": True,
            }
        }
