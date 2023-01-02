from tortoise.contrib.pydantic import pydantic_model_creator


class FastTable:
    def __init__(self, model):
        from fastadmin.resources import FastResource
        self.model = model
        self.pydantic_model = pydantic_model_creator(model, name=model.__name__)
        self.base_resource = FastResource(self)

    async def create_item(self, **kwargs):
        return self.model.create(**kwargs)

    async def get_item(self, id: str):
        return self.pydantic_model.from_orm(await self.model.get(id=id))

    async def get_item_list(self):
        return [self.pydantic_model.from_orm(item) for item in await self.model.all()]

    def get_resources(self):
        return [self.base_resource]
