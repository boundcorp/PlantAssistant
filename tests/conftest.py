from dataclasses import dataclass
import pytest
from httpx import AsyncClient
from tortoise import Tortoise
from tortoise.queryset import QuerySetSingle

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