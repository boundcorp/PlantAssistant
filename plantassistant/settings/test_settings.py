from .defaults import TORTOISE_ORM

TORTOISE_INMEMORY_TEST = dict(
    **TORTOISE_ORM,
)
TORTOISE_INMEMORY_TEST["connections"]["default"] = "sqlite://:memory:"
