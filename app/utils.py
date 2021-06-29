import os
import uuid

import aiofiles
from pydantic import BaseModel

project_root_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(project_root_path, "../data")

if not os.path.isdir(data_path):
    os.mkdir(data_path)


class ValidationException(Exception):
    def __init__(self, exception):
        self.errors_out = convert_error_pydantic(
            exception.errors()
        )  # use with pydantic validation
        # self.errors_out = utils.convert_error_marshmallow(exception.__dict__['messages']) # use with marshmallow validation


def save_file(file):
    filename = str(uuid.uuid4())
    file_path = os.path.join(data_path, filename)

    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())
    return file_path


async def save_file_aiof(file):
    filename = str(uuid.uuid4())
    file_path = os.path.join(data_path, filename)

    async with aiofiles.open(file_path, "wb") as out:
        contents = await file.read()
        await out.write(contents)
    return file_path


def convert_error_marshmallow(error):
    error_fields = []
    for key in error:
        message = "".join(error[key])
        error_fields.append({key: {"message": message}})
    return {"type": "ValidationError", "message": None, "fields": error_fields}


def convert_error_pydantic(exc):
    error_fields = []
    for data in exc:
        temp_field = data["loc"][1] if len(data["loc"]) > 1 else data["loc"][0]
        temp_field = "common" if temp_field == "__root__" else temp_field
        temp_mes = data["msg"]
        error_fields.append({temp_field: {"message": temp_mes}})
    return {"type": "ValidationError", "message": None, "fields": error_fields}


# declaring a class
class dict2obj:
    def __init__(self, d):
        self.__dict__["d"] = d

    def __getattr__(self, key):
        value = self.__dict__["d"][key]
        if isinstance(type(value), type({})):
            return dict2obj(value)

        return value


class Example_200(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "base64_string": "UklGRrQBAABXRUJQVlA4WAoAAAAQAAAAMQAAGwAAQUxQSCIAAAABF7D9EREBo7aRJM21i3AMcoN2nxH9jwuA+VVVVe9PvACYVlA4IGwBAAAQBwCdASoyABwAPm02l0gkIyIhJApIgA2JZz5owtVXjtBBBHiINLjBN5jWSk49bfuJCqbYWZ7XW1WgnN6Clg6KAAD+2+qf9rnRIkhj5SmyCEU/2vDv4WLuPCtPZ0z85RPS9UT/DdgDiJb6ct90KwpiwVQimg8xQS/VYxIvE9M8po5eIS3LUblYCy8DzHHoQfeplwBKR5JWqHnspQID7fH2iHg8S3aXsGev4FcljKc9mrRQfMAszhNlGzyPnHoMAxDvX8ch1K+4YcuHbl+ST6UyvgPQBvc+Xrptb7SSE3y4zr7bfk38PYavkTlPun5O4+HfJ5KPZ+Eo9Hevw7jNfWN7F7C9C6FRCPRynuyu76+TGhZBN/7Te4OYrgYAaGqqr4s0jDFxgY9RRSZKF47gokXqE8dQsPaAAMgMfW0FPf/pIp9gv1k9fhLEXk3p4lpLZnsESgWs703hpIm9x99VsTEkMFwZOunZvlN+QAAA",
                    "reference_id": "abcd12",
                    "time_stamp": "2021-03-31T14:26:13",
                    "process_time": 0.08904647827148438,
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
                    "message": "null",
                    "fields": [
                        {"reference_id": {"message": "field required"}},
                        {"image_file": {"message": "field required"}},
                    ],
                },
                "status": "failed",
            }
        }


class Example_504(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "data": "null",
                "error": {
                    "type": "TimeoutError",
                    "message": "API timed out.",
                    "fields": "null",
                },
                "status": "failed",
            }
        }
