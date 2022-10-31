import os
from typing import Union

PROJECT_NAME = "plantassistant"

INSTALLED_APPS = [
    "aerich",
    "plantassistant.app.users",
    "plantassistant.app.locations",
    "plantassistant.app.plants",
    "plantassistant.app.schemes",
]

SECRET_KEY = os.environ.get("SECRET_KEY", "-")

# Defaults to dev
ENVIRONMENT: Union["dev", "production", "staging"] = os.environ.get("ENVIRONMENT", "dev")

# Defaults to true in dev, false otherwise
DEBUG = os.environ.get("DEBUG", ENVIRONMENT == "dev")

if ENVIRONMENT != "dev" and SECRET_KEY == "-":
    raise ValueError("SECRET_KEY must be set in production")

# Default to persists on disk
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///data/db.sqlite3")

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

BACKEND_CORS_ORIGINS = []
LOG_LEVEL = "INFO"

TIMEZONE = os.environ.get("TZ", "UTC")
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": [f"{app}.models" for app in INSTALLED_APPS],
            "default_connection": "default",
        }
    },
    "timezone": TIMEZONE,
    "routers": ["plantassistant.db.DefaultRouter"],
}

# Frequency each entity is allowed to update from HA
# If this is set to 1 minute and you have 1000 entities,
# you will have 1000 requests per minute to HA
HOMEASSISTANT_ENTITY_UPDATE_FREQUENCY = 60