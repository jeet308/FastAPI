from marshmallow import Schema, fields, validate, ValidationError, validates
from datetime import datetime


class ImageSchema(Schema):
    reference_id = fields.Str(example="Foo",
        required=True,
        error_messages={"type":"validation_error",
                        "field":"reference_id",
                        "message": "reference_id is required."},
        validate=[validate.Length(equal=6)])
    resize_width = fields.Int(required=True,
        validate=validate.Range(min=1, max=1920),
        error_messages={"type":"validation_error",
                        "field":"resize_width",
                        "message": "resize_width is required."})
    company_name = fields.Str(required=True,
        validate=validate.Length(min=1, max=30),
        error_messages={"type":"validation_error",
                        "field":"company_name",
                        "message": "company_name is required."})
    image_format = fields.Str()
    quality_check = fields.Bool()

    @validates("image_format")
    def validate_quantity(self, value):
        if value not in ['jpg', 'jpeg', 'png']:
            raise ValidationError({"type":"validation_error",
                                   "field":"reference_id",
                                   "message": f"{value} image_format is not supported"})

    @validates("reference_id")
    def reference_id_validate(self, value):
        if not value.isalnum():
            raise ValidationError({"type":"validation_error",
                                   "field":"reference_id",
                                   "message": "reference_id must be alphanumeric"})

   


