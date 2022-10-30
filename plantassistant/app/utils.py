import os

from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from pydantic import BaseModel

# This must be set in production! We would normally raise an error if no value was provided, but
# using a default "test secret" value is easier in development for this demonstration project
SECRET_KEY = os.environ.get("SECRET_KEY", "test secret")
ALGORITHM = os.environ.get("SECRET_ALGORITHM", "HS256")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(input: str):
    return pwd_context.hash(input)


def check_password(input: str, hash: str):
    return pwd_context.verify(input, hash)


class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False


@AuthJWT.load_config
def get_config():
    return Settings()
