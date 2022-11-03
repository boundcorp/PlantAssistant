import enum

from tortoise import fields, models

from plantassistant.app import common
from plantassistant.app.locations.models import Property


class SensorAttributes(enum.Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    SOIL_MOISTURE = "soil_moisture"
    LUX = "lux"
    UV = "uv"


class Planting(models.Model, common.UUID, common.Timestamp, common.Name):
    """
    A Planting is a group of the same kind of plants that are planted together
    """
    garden = fields.ForeignKeyRelation["Garden"](
        "models.Garden", related_name="plantings"
    )
    scheme = fields.ForeignKeyRelation["Scheme"](
        "models.Scheme", related_name="plantings"
    )
    start_date = fields.DateField(null=True)
    end_date = fields.DateField(null=True)

    async def get_sensor_readings(self):
        return {sensor.attribute: await sensor.get_reading()
                for sensor in await PlantingSensor.filter(planting_id=self.pk).all()}


class PlantingSensor(models.Model, common.UUID, common.Timestamp):
    """
    A PlantingSensor is a sensor that is attached to a Planting
    """
    planting = fields.ForeignKeyRelation["Planting"](
        "models.Planting", related_name="sensors"
    )

    attribute = fields.CharEnumField(SensorAttributes, null=True)
    ha_sensor_path = fields.CharField(max_length=255)

    async def get_reading(self):
        if "#" in self.ha_sensor_path:
            entity_id, attribute = self.ha_sensor_path.split("#")
        else:
            entity_id = self.ha_sensor_path
            attribute = None

        property = await Property.filter(gardens__plantings__sensors__id=self.pk).first()
        state = await property.ha_getstate(entity_id)
        if attribute:
            if attribute in state["attributes"]:
                return state["attributes"][attribute]
            elif attribute in state:
                return state[attribute]
        else:
            return state["state"]


class PlantingSensorReading(models.Model, common.UUID):
    """
    A PlantingSensorReading is a reading from a PlantingSensor
    """
    planting_sensor = fields.ForeignKeyRelation["PlantingSensor"](
        "models.PlantingSensor", related_name="readings"
    )

    reading_at = fields.DatetimeField(index=True)
    value_float = fields.FloatField(null=True)
