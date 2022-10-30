from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "email" VARCHAR(20) NOT NULL UNIQUE,
    "password_hash" VARCHAR(128),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "user"."email" IS 'This is a username';
COMMENT ON TABLE "user" IS 'The User model';
CREATE TABLE IF NOT EXISTS "property" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "homeassistant_url" VARCHAR(2048) NOT NULL,
    "homeassistant_token" VARCHAR(1024) NOT NULL,
    "owner_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "property" IS 'The Property model corresponds to a HomeAssistant installation';
CREATE TABLE IF NOT EXISTS "garden" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "enclosure" VARCHAR(7) NOT NULL  DEFAULT 'OUTDOOR',
    "ha_zone_entity_id" VARCHAR(255) NOT NULL,
    "ha_weather_entity_id" VARCHAR(255) NOT NULL,
    "property_id" UUID NOT NULL REFERENCES "property" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "garden"."enclosure" IS 'INDOOR: INDOOR\nOUTDOOR: OUTDOOR';
COMMENT ON TABLE "garden" IS 'Each Garden is a distinct area within a Property, like a yard, greenhouse or indoor space';
CREATE TABLE IF NOT EXISTS "planting" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "recipe" JSONB NOT NULL,
    "start_date" DATE,
    "end_date" DATE,
    "garden_id" UUID NOT NULL REFERENCES "garden" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "planting" IS 'A Planting is a group of the same kind of plants that are planted together';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
