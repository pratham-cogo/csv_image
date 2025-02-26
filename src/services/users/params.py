from pydantic import BaseModel, model_validator

class CreateUser(BaseModel):
    username: str
    password: str

    @model_validator(mode='before')
    def validate_username(cls, values):
        username = values.get('username')
        if username and not username.isalnum():
            raise ValueError("Username must be alphanumeric.")
        return values

class LoginUser(BaseModel):
    username: str
    password: str

    @model_validator(mode='before')
    def validate_username(cls, values):
        username = values.get('username')
        if username and not username.isalnum():
            raise ValueError("Username must be alphanumeric.")
        return values
