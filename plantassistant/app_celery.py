from celery import Celery
from plantassistant.settings import REDIS_URL, PROJECT_NAME
from logging import getLogger
log = getLogger()

celery_app = Celery(PROJECT_NAME, broker=REDIS_URL)

celery_app.conf.beat_schedule = {
    'update-plant-status': {
        'task': 'plantassistant.celery.update_plant_status',
        'schedule': 300.0,
    }
}

@celery_app.task
def update_plant_status():
    return "Updating plant status"