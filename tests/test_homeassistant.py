from unittest.mock import MagicMock

import pytest
import os
import requests

from plantassistant.app.locations.constants import GardenEnclosure
from plantassistant.app.locations.models import Property, Garden
from tests.conftest import CommonScenario

HA_URL = os.environ.get("HA_URL", "")
HA_TOKEN = os.environ.get("HA_TOKEN", "")
HA_HEADERS = {"Authorization": "Bearer " + HA_TOKEN, "Content-Type": "application/json"}


def ha_get(path, **kwargs):
    return requests.get(HA_URL + path, headers=HA_HEADERS, **kwargs)


def skip_unless_ha(callable):
    return pytest.mark.skipif(not HA_URL or not HA_TOKEN, reason="HA_URL and HA_TOKEN must be set to run HA tests")(
        callable)


@skip_unless_ha
@pytest.mark.anyio
async def test_hass_api():
    result = ha_get("/api/states").json()
    ids = [state["entity_id"] for state in result]
    assert "person.plant_tester" in ids
    assert "zone.home" in ids
    assert "sun.sun" in ids


@skip_unless_ha
@pytest.mark.anyio
async def test_home_garden_weather(common_scenario: CommonScenario):
    property = await Property.create(name="Test Home",
                                     owner=common_scenario.test_user,
                                     homeassistant_url=HA_URL,
                                     homeassistant_token=HA_TOKEN)
    garden = await Garden.create(name="Test Outdoor Garden", property=property, enclosure=GardenEnclosure.OUTDOOR,
                                 ha_zone_entity_id="zone.home", ha_weather_entity_id="weather.home")
    assert await garden.get_weather() == 'cloudy'
