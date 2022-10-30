import logging

from typing import Type

from tenacity import retry, stop_after_attempt, wait_fixed, before_log, after_log
from tortoise import Model, BaseDBAsyncClient, connections
from plantassistant.settings import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)


class DefaultRouter:
    def db_for_read(self, model: Type[Model]):
        return "default"

    def db_for_write(self, model: Type[Model]):
        return "default"


max_tries = 60 * 5  # 5 minutes
wait_seconds = 1
@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def attempt_db_connection() -> None:
    try:
        conn: BaseDBAsyncClient = connections.get("default")
        # Try to create session to check if DB is awake
        conn.execute_query("SELECT 1")
    except Exception as e:
        logger.error(e)
        raise e


def wait_for_db() -> None:
    logger.info("Initializing service")
    attempt_db_connection()
    logger.info("Service finished initializing")
