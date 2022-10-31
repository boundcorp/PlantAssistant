import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta

import jwt
import pytest
import yaml
from httpx import AsyncClient
from tortoise import Tortoise
from tortoise.queryset import QuerySetSingle

from plantassistant.app.locations.constants import GardenEnclosure
from plantassistant.app.locations.models import Property, Garden
from plantassistant.main import app
from plantassistant.app.users.models import User

DB_URL = "sqlite://:memory:"
TEST_USER = {"email": "test@test.com", "password": "test123!!"}


async def init_db(db_url, create_db: bool = False, schemas: bool = False) -> None:
    """Initial database connection"""
    from plantassistant.settings.test_settings import TORTOISE_INMEMORY_TEST
    await Tortoise.init(config=TORTOISE_INMEMORY_TEST, _create_db=create_db)
    if create_db:
        print(f"Database created! {db_url = }")
    if schemas:
        await Tortoise.generate_schemas()
        print("Success to generate schemas")


async def init(db_url: str = DB_URL):
    await init_db(db_url, True, True)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        print("Client is ready")
        yield client


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    await init()
    yield
    await Tortoise._drop_databases()


@dataclass
class CommonScenario:
    client: AsyncClient
    test_user: User
    test_user_password: str


@pytest.fixture(scope="session")
async def common_scenario(client: AsyncClient):
    """
    The common scenario always consists of a single user, logged in, and the API client
    """
    await client.post("/register", json=TEST_USER)
    test_user: QuerySetSingle[User] = await User.get(email=TEST_USER['email'])

    # Create the test client cookies for this user to be logged in
    await client.post("/login", json=dict(email=test_user.email,
                                          password=TEST_USER['password']))

    return CommonScenario(
        client=client,
        test_user=test_user,
        test_user_password=TEST_USER['password'],
    )


def load_api_token_from_fixture(fixture_name):
    with open(f"docker/homeassistant/{fixture_name}/auth") as f:
        auth = json.load(f)
        api_keys = [token for token in auth["data"]["refresh_tokens"] if
                    token["token_type"] == "long_lived_access_token"]
        now = datetime.utcnow()
        if api_keys:
            key = api_keys[0]
            return jwt.encode(
                {
                    "iss": key["id"],
                    "iat": now,
                    "exp": now + timedelta(days=365),
                },
                key["jwt_key"],
                algorithm="HS256"
            ).decode('ascii')


HA_URL = os.environ.get("HA_URL", "")
HA_TOKEN = load_api_token_from_fixture("empty_instance") or os.environ.get("HA_TOKEN", "")
HA_HEADERS = {"Authorization": "Bearer " + HA_TOKEN, "Content-Type": "application/json"}


@dataclass
class GardenScenario(CommonScenario):
    property: Property
    garden: Garden


@pytest.fixture(scope="session")
async def simple_garden(common_scenario: CommonScenario):
    """
    Register the home property and create a herb garden on an indoor windowsill
    """
    _property = await Property.create(name="Test Home",
                                     owner_id=common_scenario.test_user.pk,
                                     homeassistant_url=HA_URL,
                                     homeassistant_token=HA_TOKEN)
    _garden = await Garden.create(name="Test Outdoor Garden", property=_property, enclosure=GardenEnclosure.OUTDOOR,
                                 ha_zone_entity_id="zone.home", ha_weather_entity_id="weather.home")

    with open('tests/fixtures/weather/basic.yaml') as fh:
        set_weather = await _property.ha_setstate(_garden.ha_weather_entity_id, yaml.safe_load(fh))

    return GardenScenario(
        **common_scenario.__dict__,
        property=_property,
        garden=_garden,
    )
