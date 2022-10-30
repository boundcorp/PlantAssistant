from tortoise import fields, models
from .. import common


class User(models.Model, common.UUID, common.Timestamp):
    """
    The User model
    """

    #: This is a username
    email = fields.CharField(max_length=200, unique=True)
    password_hash = fields.CharField(max_length=128, null=True)

    class PydanticMeta:
        exclude = ["password_hash"]
