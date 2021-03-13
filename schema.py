from marshmallow import Schema, fields, validate, ValidationError, validates
from datetime import datetime 

class ImageSchema(Schema):
    reference_id = fields.Str(required=True, error_messages={"required": "reference_id is required."}, validate=[validate.Length(equal=6)])
    resize_width = fields.Int(required=True,validate=validate.Range(min=1,max=1920),error_messages={"required": "resize_width is required."})
    company_name = fields.Str(required=True,validate=validate.Length(min=1,max=30),error_messages={"required": "company_name is required."})
    image_format = fields.Str()
    quality_check = fields.Bool()

    @validates("image_format")
    def validate_quantity(self,value):
        if value not in ['jpg','jpeg','png']:
            raise ValidationError(f"{value} image_format is not supported")

    @validates("reference_id")
    def reference_id_validate(self,value):
        if not value.isalnum():
            raise ValidationError('reference_id must be alphanumeric')
