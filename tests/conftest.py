import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

import jwt
import pytest
import yaml
import logging
from httpx import AsyncClient
from tortoise import Tortoise
from tortoise.queryset import QuerySetSingle

from plantassistant.app.locations.constants import GardenEnclosure
from plantassistant.app.locations.models import Property, Garden
from plantassistant.app.plants.models import Planting, SensorAttributes, PlantingSensor
from plantassistant.app.schemes.models import Scheme
from plantassistant.app_setup import app
from plantassistant.app.users.models import User

log = logging.getLogger()

DB_URL = "sqlite://:memory:"
TEST_USER = {"email": "test@test.com", "password": "test123!!"}


async def init_db(db_url, create_db: bool = False, schemas: bool = False) -> None:
    """Initial database connection"""
    from plantassistant.settings.test_settings import TORTOISE_INMEMORY_TEST
    await Tortoise.init(config=TORTOISE_INMEMORY_TEST, _create_db=create_db)
    if create_db:
        log.info(f"Database created! {db_url = }")
    if schemas:
        await Tortoise.generate_schemas()
        log.info("Success to generate schemas")


async def init(db_url: str = DB_URL):
    await init_db(db_url, True, True)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
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
        log.info(f"Loading API token from docker/homeassistant/{fixture_name}")
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
async def indoor_garden(common_scenario: CommonScenario):
    """
    Register the home property and create a garden
    """
    property_obj = await Property.create(
        name="Test Home",
        owner_id=common_scenario.test_user.pk,
        homeassistant_url=HA_URL,
        homeassistant_token=HA_TOKEN)

    with open('tests/fixtures/weather/basic.yaml') as fh:
        set_garden_weather = yaml.safe_load(fh)

    garden = await Garden.create(
        name="Test Indoor Garden",
        property=property_obj,
        enclosure=GardenEnclosure.INDOOR,
        ha_zone_entity_id="zone.home",
        ha_weather_entity_id="weather.home",
        ha_weather=set_garden_weather,  # prepopulate the weather
    )

    return GardenScenario(
        **common_scenario.__dict__,
        property=property_obj,
        garden=garden,
    )


@pytest.fixture(scope="session")
async def outdoor_garden(common_scenario: CommonScenario):
    """
    Register the home property and create a garden
    """
    property_obj = await Property.create(
        name="Test Home",
        owner_id=common_scenario.test_user.pk,
        homeassistant_url=HA_URL,
        homeassistant_token=HA_TOKEN)

    with open('tests/fixtures/weather/basic.yaml') as fh:
        set_garden_weather = yaml.safe_load(fh)

    garden = await Garden.create(
        name="Test Outdoor Garden",
        property=property_obj,
        enclosure=GardenEnclosure.OUTDOOR,
        ha_zone_entity_id="zone.home",
        ha_weather_entity_id="weather.home",
        ha_weather=set_garden_weather,  # prepopulate the weather
    )

    return GardenScenario(
        **common_scenario.__dict__,
        property=property_obj,
        garden=garden,
    )


@dataclass
class PlantingScenario(GardenScenario):
    plantings: List[Planting]


@pytest.fixture(scope="session")
async def outdoor_fruits(outdoor_garden: GardenScenario):
    """
    Create a planting of some outdoor fruits
    """
    fruits_scheme = await Scheme.create(name="Outdoor Fruits", owner_id=outdoor_garden.test_user.pk)
    tomato = await Planting.create(name="Tomato", garden=outdoor_garden.garden, scheme=fruits_scheme)
    await PlantingSensor.create(name="Tomato Temperature Sensor", planting=tomato,
                                attribute=SensorAttributes.TEMPERATURE, ha_sensor_path="weather.home#temperature")

    return PlantingScenario(
        **outdoor_garden.__dict__,
        plantings=[tomato]
    )


@pytest.fixture(scope="session")
async def indoor_herbs(indoor_garden):
    """
    Create a planting of some indoor herbs
    """
    herbs_scheme = await Scheme.create(name="Indoor Herbs", owner_id=indoor_garden.test_user.pk)
    herbs = await Planting.create(name="Basil", garden=indoor_garden.garden, scheme=herbs_scheme)
    #await PlantingSensor.create(name="Basil Temperature Sensor", planting=herbs, attribute=SensorAttributes.TEMPERATURE)
    # TODO: Add a sensor to the planting

    return PlantingScenario(
        **indoor_garden.__dict__,
        plantings=[herbs, ]
    )
