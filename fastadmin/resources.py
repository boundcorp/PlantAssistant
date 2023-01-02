from typing import Type, List

import strawberry
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from fastadmin.tables import FastTable
from fastadmin.utils import to_snake_case, to_camel_case


class FastResource:
    resource_name: str
    pydantic_output: Type[BaseModel]
    pydantic_input: Type[BaseModel]
    strawberry_output: strawberry.type
    strawberry_input: strawberry.type
    table: "FastTable"

    def __init__(self, table, resource_name: str = None, output_model: Type[BaseModel] = None,
                 input_model: Type[BaseModel] = None):
        self.table = table
        self.resource_name = resource_name or to_snake_case(self.table.model.__name__)
        self.pydantic_output = output_model or pydantic_model_creator(self.table.model, name=self.resource_name)
        self.pydantic_input = input_model or pydantic_model_creator(self.table.model,
                                                                    name=f"{self.resource_name}_input")
        self.strawberry_output = strawberry.experimental.pydantic.type(model=self.pydantic_output,
                                                                       name=self.make_type_name(),
                                                                       all_fields=True
                                                                       )(type(self.resource_name, (object,), {}))

        self.strawberry_input = strawberry.experimental.pydantic.input(model=self.pydantic_input,
                                                                       name=self.make_type_name("input"),
                                                                       all_fields=True
                                                                       )(type(self.resource_name, (object,), {}))

    def make_type_name(self, suffix="", prefix="", capitalize_first=True):
        return to_camel_case((prefix and prefix+"_" or "") + self.resource_name + "_" + suffix, capitalize_first)

    def make_resolver_name(self, prefix=""):
        return self.make_type_name(prefix=prefix, capitalize_first=False)

    def resolver_for_create_mutation(self):
        Output = self.strawberry_output
        Input = self.strawberry_input

        async def create_item(input: Input) -> Output:
            created = await self.table.model.create(**{k: v for k, v in input.__dict__.items() if v})
            return self.strawberry_output.from_pydantic(self.pydantic_output.from_orm(created))

        return strawberry.field(resolver=create_item)

    def resolver_for_get_item(self):
        strawberry_type = self.strawberry_output

        async def lookup_item(id: str) -> strawberry_type:
            return self.strawberry_output.from_pydantic(await self.table.get_item(id))

        return strawberry.field(resolver=lookup_item)

    def resolver_for_get_list(self):
        strawberry_type = self.strawberry_output

        @strawberry.type(name=self.make_type_name("list_result"))
        class ListResult:
            items: List[strawberry_type]
            total: int

        async def lookup_list() -> ListResult:
            items = await self.table.get_item_list()
            return ListResult(items=[self.strawberry_output.from_pydantic(item) for item in items], total=len(items))

        return strawberry.field(resolver=lookup_list)

    def get_queries(self):
        return {
            self.make_resolver_name("get"): self.resolver_for_get_item(),
            self.make_resolver_name("list"): self.resolver_for_get_list(),
        }

    def get_mutations(self):
        return {
            self.make_resolver_name(prefix="create"): self.resolver_for_create_mutation(),
        }

    def get_schema(self):
        return dict(**{
            resolver.python_name: {
                "type": resolver.type.__name__,
                "query": to_camel_case(name),
                "description": resolver.description,
                "args": [arg.python_name for arg in resolver.arguments],
                # "deprecation_reason": resolver.deprecation_reason,
            }
            for name, resolver in [*self.get_queries().items(),
                                   *self.get_mutations().items(),
                                   ]
        }, model=self.pydantic_output.schema())
