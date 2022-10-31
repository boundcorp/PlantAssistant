from enum import Enum
from typing import Optional, List

from tortoise.contrib.pydantic import PydanticModel


class RuleMethods(str, Enum):
    MINIMUM_TEMP = "core.MinimumTemp"


class RuleMethod(PydanticModel):
    name: str
    arguments: Optional[List[str]]
    description: Optional[str]
    sensor: Optional[str]
    operator: Optional[str]
    value: Optional[str]
    unit: Optional[str]
    triggers: Optional[str]
