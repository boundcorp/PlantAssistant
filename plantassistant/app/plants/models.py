from tortoise import fields, models

from plantassistant.app import common


class Planting(models.Model, common.UUID, common.Timestamp, common.Name):
    """
    A Planting is a group of the same kind of plants that are planted together
    """
    garden = fields.ForeignKeyRelation["Garden"](
        "models.Garden", related_name="plantings"
    )
    recipe = fields.JSONField(default={})
    start_date = fields.DateField(null=True)
    end_date = fields.DateField(null=True)