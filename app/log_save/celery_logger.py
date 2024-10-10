import os
import logging
from celery import Celery
from celery.signals import after_setup_logger

from app.log_save.celery_tasks import send_notification
from app.log_save.level_log import logging_level

if not os.path.exists('logs'):
   os.makedirs('logs')

logging.basicConfig(
    filename='logs/app.log',
    level=logging_level ,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d/%m/%Y %I:%M:%S %p'
)
logger = logging.getLogger(__name__)


celery = Celery(
    __name__,
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0'
)

@after_setup_logger.connect
def setup_celery_logger(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("tasks")
    fh = logging.FileHandler('logs/celery_tasks.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
