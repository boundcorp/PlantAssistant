from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from plantassistant.app.users.models import User
from plantassistant.app.users.schema.types import (User_Pydantic,
                                                   UserLoginInput,
                                                   UserRegisterInput)
from plantassistant.app.utils import check_password, hash_password

users_router = APIRouter()

async def LoginRequired(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return await User.get(email=Authorize.get_jwt_subject())

@users_router.post("/register", response_model=User_Pydantic)
async def register(input: UserRegisterInput):
    # We should regex here to ensure password complexity
    # but we will keep the demo simple and just test length
    if len(input.password) < 8:
        raise HTTPException(status_code=400, detail="Password too simple")

    password_hash = hash_password(input.password)

    try:
        user_obj = await User.create(email=input.email, password_hash=password_hash)
    except Exception as e:
        print(e)
        # It would be nicer to check for username collisions to return a friendly validation error
        raise HTTPException(status_code=400, detail="Error creating your account")

    return await User_Pydantic.from_tortoise_orm(user_obj)


@users_router.post("/login", response_model=User_Pydantic)
async def login(input: UserLoginInput, Authorize: AuthJWT = Depends()):
    user = await User.get(email=input.email)

    # Authentication for hashed password
    if not check_password(input.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create the tokens and passing to set_access_cookies or set_refresh_cookies
    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)

    # Set the JWT cookies in the response
    # They are saved as httponly cookies, for security!
    # https://indominusbyte.github.io/fastapi-jwt-auth/usage/jwt-in-cookies/
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return await User_Pydantic.from_tortoise_orm(user)


@users_router.post("/refresh")
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)

    # Set the JWT cookies in the response
    Authorize.set_access_cookies(new_access_token)
    return {"msg": "The token has been refresh"}


@users_router.delete("/logout")
def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()

    return {"msg": "Successfully logout"}


@users_router.get("/profile", response_model=User_Pydantic)
async def profile(user: User = Depends(LoginRequired)):
    return await User_Pydantic.from_tortoise_orm(user)
