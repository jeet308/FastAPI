from typing import Optional

from pydantic import BaseModel, validator


class ClientSchema(BaseModel):

    username: str
    password: str

    @validator("username")
    def company_name_validate(cls, v):
        if not v.isalpha():
            raise ValueError("company_name must be alphabetic only")
        if len(v) < 0 and len(v) < 30:
            raise ValueError("company_name length must between 1 to 30 characters")
        return v

    @validator("password")
    def password_validate(cls, v):
        if len(v) < 8 and len(v) < 16:
            raise ValueError("password length must between 8 to 15 characters")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
