from typing import List

import strawberry
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON
from tortoise.contrib.fastapi import register_tortoise

from fastadmin.tables import FastTable
from plantassistant.settings import TORTOISE_ORM

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001"
]

app = FastAPI(title="FastAdmin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_tables():
    from plantassistant.app.users.models import User
    from plantassistant.app.locations.models import Property
    return [
        FastTable(model)
        for model in [User, Property]
    ]


tables = generate_tables()


@strawberry.type
class TableOutput:
    name: str
    resources: JSON


FastAdminQuery = strawberry.type(type("FastAdminQuery", (), dict(**{
    name: resolver
    for table in tables
    for resource in table.get_resources()
    for name, resolver in resource.get_queries().items()
})))

FastAdminMutation = strawberry.type(type("FastAdminMutation", (), dict(**{
    name: resolver
    for table in tables
    for resource in table.get_resources()
    for name, resolver in resource.get_mutations().items()
})))


def describe_schema():
    return [
            TableOutput(name=table.model.__name__,
                        resources=[resource.get_schema() for resource in table.get_resources()])
            for table in generate_tables()
        ]

@strawberry.type
class Query(FastAdminQuery):
    @strawberry.field
    def get_tables(self, info) -> List[TableOutput]:
        return describe_schema()

with open("schema.graphql", "w+") as f:
    f.write(strawberry.Schema(query=Query, mutation=FastAdminMutation).as_str())


schema = strawberry.Schema(Query, mutation=FastAdminMutation)

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

register_tortoise(
    app=app,
    config=TORTOISE_ORM,
)
