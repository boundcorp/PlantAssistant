from tortoise import fields


class UUID:
    id = fields.UUIDField(pk=True)


class Timestamp:
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    modified_at = fields.DatetimeField(null=True, auto_now=True)


class Name:
    name = fields.CharField(max_length=255)
