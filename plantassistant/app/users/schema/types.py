from typing import Union

from tortoise.contrib.pydantic import PydanticModel, pydantic_model_creator

from plantassistant.app.users.models import User


class UserRegisterInput(PydanticModel):
    email: str
    password: str


class UserLoginInput(PydanticModel):
    email: str
    password: str


class Token(PydanticModel):
    access_token: str
    token_type: str


class TokenData(PydanticModel):
    email: Union[str, None] = None


class LoginSuccess(PydanticModel):
    token: Token
    user: TokenData


User_Pydantic = pydantic_model_creator(User, name="User")
