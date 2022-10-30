from tortoise.contrib.pydantic import pydantic_model_creator

from ..models import Property, Garden

Property_Pydantic = pydantic_model_creator(Property, name="Property")
Garden_Pydantic = pydantic_model_creator(Garden, name="Garden")
