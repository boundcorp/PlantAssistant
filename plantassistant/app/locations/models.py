import yaml.reader
from tortoise import fields, models
import requests

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

    def get_ha(self, path, **kwargs):
        return requests.get(self.homeassistant_url + path, headers=self.ha_headers, **kwargs)

    def post_ha(self, path, **kwargs):
        return requests.post(self.homeassistant_url + path, headers=self.ha_headers, **kwargs)


class Garden(models.Model, common.UUID, common.Timestamp, common.Name):
    """
    Each Garden is a distinct area within a Property, like a yard, greenhouse or indoor space
    """

    property = fields.ForeignKeyRelation["Property"](
        "models.Property", related_name="gardens"
    )

    enclosure = fields.CharEnumField(GardenEnclosure, default=GardenEnclosure.OUTDOOR)
    ha_zone_entity_id = fields.CharField(max_length=255, null=True)
    ha_weather_entity_id = fields.CharField(max_length=255, null=True)

    async def get_weather(self):
        property = await self.property.get()
        with open('tests/fixtures/weather/basic.yaml') as fh:
            data = yaml.safe_load(fh)
            set_weather = property.post_ha(f"/api/states/{self.ha_weather_entity_id}", json=data)
        weather = property.get_ha(f"/api/states/{self.ha_weather_entity_id}").json()

        return weather["state"]
