from marshmallow import Schema, fields, validate, ValidationError, validates
from datetime import datetime
from pydantic import BaseModel

class ImageSchema(Schema):
    reference_id = fields.Str(
        required=True,
        error_messages={
            "message": "reference_id is required."},
        validate=[validate.Length(equal=6)])

    resize_with_width = fields.Bool()

    resize_width = fields.Int(required=True,
                              validate=validate.Range(min=1, max=1920),
                              error_messages={
                                  "message": "resize_width is required."})

    resize_height = fields.Int(required=True,
                              validate=validate.Range(min=1, max=1920),
                              error_messages={
                                  "message": "resize_height is required."})
    
    company_name = fields.Str(required=True,
                              validate=validate.Length(min=1, max=30),
                              error_messages={
                                  "message": "company_name is required."})
    image_format = fields.Str()
    quality_check = fields.Bool()

    @validates("image_format")
    def validate_quantity(self, value):
        if value not in ['jpg', 'jpeg', 'png']:
            raise ValidationError({
                "message": f"{value} image_format is not supported"})

    @validates("reference_id")
    def reference_id_validate(self, value):
        if not value.isalnum():
            raise ValidationError({
                "message": "reference_id must be alphanumeric"})


class Example(BaseModel):

    class Config:
        schema_extra = {
            "example": {
                "reference_id":  "abcd12",
                "resize_with_width":True,
                "resize_width":  1250,
                "resize_height": 500,
                "company_name":  "frslabs",
                "image_format":  "png",
                "quality_check": True,
            }
        }
