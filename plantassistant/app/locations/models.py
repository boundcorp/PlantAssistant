import httpx
import requests
from tortoise import fields, models

from plantassistant.app import common
from plantassistant.app.locations.constants import GardenEnclosure


class Property(models.Model, common.UUID, common.Timestamp, common.Name):
    """
    The Property model corresponds to a HomeAssistant installation
    """

    owner = fields.ForeignKeyRelation["User"](
        "models.User", related_name="properties"
    )

    homeassistant_url = fields.CharField(max_length=2048, null=True)
    homeassistant_token = fields.CharField(max_length=1024, null=True)

    @property
    def ha_headers(self):
        return {"Authorization": "Bearer " + self.homeassistant_token, "Content-Type": "application/json"}

    async def ha_get(self, path, **kwargs):
        async with httpx.AsyncClient() as client:
            result = await client.get(self.homeassistant_url + path, headers=self.ha_headers, **kwargs)
            return result.json()

    async def ha_post(self, path, data_json, **kwargs):
        async with httpx.AsyncClient() as client:
            result = await client.post(self.homeassistant_url + path, json=data_json, headers=self.ha_headers, **kwargs)
            return result.json()

    async def ha_setstate(self, entity_id, state_data):
        return await self.ha_post(f"/api/states/{entity_id}", state_data)

    async def ha_getstate(self, entity_id=""):
        return await self.ha_get(f"/api/states/{entity_id}")


class Garden(models.Model, common.UUID, common.Timestamp, common.Name):
    """
    Each Garden is a distinct area within a Property, like a yard, greenhouse or indoor space
    """

    property = fields.ForeignKeyRelation["Property"](
        "models.Property", related_name="gardens"
    )

    enclosure = fields.CharEnumField(GardenEnclosure, default=GardenEnclosure.OUTDOOR)
    ha_zone_entity_id = fields.CharField(max_length=255, null=True)
    ha_zone = fields.JSONField(null=True)
    ha_weather_entity_id = fields.CharField(max_length=255, null=True)
    ha_weather = fields.JSONField(null=True)

    async def ha_update(self):
        property = await self.property.filter(id=self.property_id).first()
        self.ha_weather = await property.ha_getstate(self.ha_weather_entity_id)
        self.ha_zone = await property.ha_getstate(self.ha_zone_entity_id)
        await self.save()