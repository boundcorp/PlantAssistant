import strawberry
from fastapi import Depends, FastAPI
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from tortoise.contrib.fastapi import register_tortoise

from plantassistant import settings
from plantassistant.app.users.models import User
from plantassistant.app.users.schema.types import User_Pydantic
from plantassistant.app.users.views import users_router
from plantassistant.settings import TORTOISE_ORM

app = FastAPI(title="Test Login with FastAPI example")


@app.get("/")
async def root(Authorize: AuthJWT = Depends()):
    return {
        "health": "ok",
        "current_user": Authorize.get_jwt_subject(),
        # TODO: Remove this full dump of the users table, this is obviously a security leak
        # but it's very handy to prove that the application is working :)
        "users": await User_Pydantic.from_queryset(User.all()),
    }


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@strawberry.type
class Query:
    @strawberry.field
    def hello(self, info) -> str:
        return "Hello, world!"


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
app.include_router(users_router)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
register_tortoise(
    app=app,
    config=TORTOISE_ORM,
)