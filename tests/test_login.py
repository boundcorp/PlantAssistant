import pytest

from httpx import AsyncClient
from plantassistant.app.users.models import User
from tests.conftest import TEST_USER, CommonScenario


@pytest.mark.anyio
async def test_register(client: AsyncClient):
    register = dict(**TEST_USER)
    email = register.pop('email').replace("@", "+test_register@")
    response = await client.post("/register", json=dict(**register, email=email))
    created = response.json()
    assert "id" in created
    assert created["email"] == email
    
    obj = await User.get(id=created["id"])
    print(str(obj.pk), created["id"])
    assert str(obj.pk) == str(created["id"])

@pytest.mark.anyio
async def test_login_denies_wrong_password(common_scenario: CommonScenario):
    response = await common_scenario.client.post("/login", json=dict(email=common_scenario.test_user.email, password="wrong"))
    assert response.status_code == 401, "Expected credentials denied"
    assert response.json()['detail'] == "Invalid credentials", "Expected credentials denied warning"


@pytest.mark.anyio
async def test_login_success(common_scenario: CommonScenario):
    response = await common_scenario.client.post("/login", json=dict(email=common_scenario.test_user.email,
        password=common_scenario.test_user_password))

    assert response.status_code == 200, "Expected login success"
    assert response.json()['email'] == TEST_USER['email'], "Expected to see my profile"
    
@pytest.mark.anyio
async def test_profile(common_scenario: CommonScenario):
    response = await common_scenario.client.get("/profile")

    assert response.status_code == 200, "Expected profile success"
    assert response.json()['email'] == TEST_USER['email'], "Expected to see my profile"

        
@pytest.mark.anyio
async def test_logout(common_scenario: CommonScenario):
    await common_scenario.client.delete("/logout")

    response = await common_scenario.client.get("/profile")
    
    assert response.status_code == 401, "Expected profile unauthorized"