import formulas as formulas
from tortoise import fields, models
from tortoise.validators import MinValueValidator

from plantassistant.app import common
from plantassistant.app.plants.models import Planting
from plantassistant.app.schemes.constants import RuleMethods


class Scheme(models.Model, common.UUID, common.Timestamp, common.Name):
    """
    A Scheme describes a recipe or playbook for growing a plant
    """
    owner = fields.ForeignKeyRelation["User"](
        "models.User", related_name="schemes"
    )

    description = fields.TextField(null=True)

    def evaluate_planting(self, planting: Planting):
        for condition in self.rules.all():
            func = formulas.Parser().ast(f"={condition}")[1].compile()
            print(func.inputs, func)
            print(func())


class Rule(models.Model, common.UUID, common.Timestamp, common.Name):
    """
    A Scheme describes a recipe or playbook for growing a plant
    """
    parent_scheme = fields.ForeignKeyRelation[Scheme](
        "models.Scheme", related_name="rules"
    )
    order_in_scheme = fields.IntField(validators=[MinValueValidator(0)])

    rule_method = fields.CharEnumField[RuleMethods]()
    arguments = fields.JSONField(null=True)
