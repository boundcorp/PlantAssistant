from tortoise.contrib.pydantic import pydantic_model_creator

from ..models import Planting

Planting_Pydantic = pydantic_model_creator(Planting, name="Planting")
