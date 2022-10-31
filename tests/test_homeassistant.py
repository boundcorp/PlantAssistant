import pytest
import yaml
import logging

from tests.conftest import GardenScenario, HA_URL, HA_TOKEN, PlantingScenario
log = logging.getLogger()


def skip_unless_ha(callable):
    return pytest.mark.skipif(not HA_URL or not HA_TOKEN, reason="HA_URL and HA_TOKEN must be set to run HA tests")(
        callable)


@skip_unless_ha
@pytest.mark.anyio
async def test_hass_api(indoor_garden):
    result = await indoor_garden.property.ha_get("/api/states")
    ids = [state["entity_id"] for state in result]
    assert "person.plant_tester" in ids
    assert "zone.home" in ids
    assert "sun.sun" in ids


@skip_unless_ha
@pytest.mark.anyio
async def test_home_garden_weather(indoor_garden):
    with open('tests/fixtures/weather/basic.yaml') as fh:
        set_weather = await indoor_garden.property.ha_setstate(indoor_garden.garden.ha_weather_entity_id, yaml.safe_load(fh))
        log.info("FORCED: updated weather fixture in HomeAssistant", set_weather)

    await indoor_garden.garden.ha_update()
    assert indoor_garden.garden.ha_weather["state"] == 'cloudy'

@pytest.mark.anyio
async def test_check_herbs_temperature(indoor_herbs: PlantingScenario):
    herbs = indoor_herbs.plantings[0]
    scheme = await herbs.scheme
    assert scheme.name == "Indoor Herbs"
