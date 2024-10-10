import os
import logging

ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')


if ENVIRONMENT == 'local':
    logging_level = logging.INFO
elif ENVIRONMENT == 'dev':
    logging_level = logging.INFO
    logging.getLogger('database').setLevel(logging.CRITICAL)
elif ENVIRONMENT == 'prod':
    logging_level = logging.ERROR
