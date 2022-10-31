import pytest

from tests.conftest import GardenScenario, HA_URL, HA_TOKEN, PlantingScenario


def skip_unless_ha(callable):
    return pytest.mark.skipif(not HA_URL or not HA_TOKEN, reason="HA_URL and HA_TOKEN must be set to run HA tests")(
        callable)


@skip_unless_ha
@pytest.mark.anyio
async def test_hass_api(simple_garden: GardenScenario):
    result = await simple_garden.property.ha_get("/api/states")
    ids = [state["entity_id"] for state in result]
    assert "person.plant_tester" in ids
    assert "zone.home" in ids
    assert "sun.sun" in ids


@skip_unless_ha
@pytest.mark.anyio
async def test_home_garden_weather(simple_garden: GardenScenario):
    await simple_garden.garden.ha_update()

    assert simple_garden.garden.ha_weather["state"] == 'cloudy'

@skip_unless_ha
@pytest.mark.anyio
async def test_check_herbs_temperature(indoor_herbs: PlantingScenario):
    await indoor_herbs.garden.ha_update()

    assert indoor_herbs.plantings[0].recipe["name"] == "Indoor Herbs"
