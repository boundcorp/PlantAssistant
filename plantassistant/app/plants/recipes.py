from dataclasses import dataclass
from typing import List, Optional, Union

from tortoise.contrib.pydantic import PydanticModel


class Condition(PydanticModel):
    name: Optional[str]
    key: str
    comparator: str
    value: str


class AnyConditions(PydanticModel):
    any: List["Rule"]


class AllConditions(PydanticModel):
    all: List["Rule"]


Rule = Union[
    Condition,
    AnyConditions,
    AllConditions,
]
Rules = List[Rule]


class Override(PydanticModel):
    if_rule: Rule
    add_wants: Optional[Rules]
    add_needs: Optional[Rules]
    # remove_wants: Optional[Rules]
    # remove_needs: Optional[Rules]


class Recipe(PydanticModel):
    """ A recipe or plan for growing plants in the garden,
    including suggested tasks, a list of the plants wants and needs, and
    a list of condition-based wants-and-needs overrides
    """
    name: str
    description: str
    wants: Optional[Rules]
    needs: Optional[Rules]
    # overrides: Optional[List[Override]]


IndoorHerbs = Recipe(
    name="Indoor Herbs",
    description="A recipe for growing herbs indoors",
    wants=[
        Condition(
            name="Soil Moisture > 50%",
            key="sensor.soil_moisture",
            comparator=">=",
            value="0.5",
        ),
        Condition(
            name="Temperature above 5C",
            key="sensor.temperature_c",
            comparator=">=",
            value="5",
        )
    ],
    needs=[
        Condition(
            name="Soil Moisture > 10%",
            key="sensor.soil_moisture",
            comparator=">=",
            value="0.1",
        ),
        Condition(
            name="Temperature above freezing",
            key="sensor.temperature_c",
            comparator=">=",
            value="0",
        )
    ]
)
