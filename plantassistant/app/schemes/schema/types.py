from tortoise.contrib.pydantic import pydantic_model_creator

from ..models import Scheme

Recipe_Pydantic = pydantic_model_creator(Scheme, name="Recipe")
