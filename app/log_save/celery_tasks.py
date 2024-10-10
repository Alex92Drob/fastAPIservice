import time
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger("tasks")


@shared_task
def send_notification(device_token: str):
    logger.info("starting background task")
    time.sleep(10)  # simulates slow network call to firebase/sns
    try:
        a=11/0  #critical part that may fail, and its analysis is important
    except Exception as e:
        logger.error(f"exception while division {e}")