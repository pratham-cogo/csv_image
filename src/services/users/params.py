from pydantic import BaseModel, model_validator

class CreateUser(BaseModel):
    username: str
    password: str

    @model_validator()
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric.")
        return v

class LoginUser(BaseModel):
    username: str
    password: str

    @model_validator()
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric.")
        return v
