import os
import json
import logging
from logging import Formatter

from app.log_save.level_log import logging_level

if not os.path.exists('logs'):
   os.makedirs('logs')

class JsonFormatter(Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record):
        json_record = {}
        json_record["message"] = record.getMessage()
        if "req" in record.__dict__:
            json_record["req"] = record.__dict__["req"]
        if "res" in record.__dict__:
            json_record["res"] = record.__dict__["res"]
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["err"] = self.formatException(record.exc_info)
        return json.dumps(json_record)



logger = logging.getLogger()
logger.setLevel(logging_level)
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())
file_handler = logging.FileHandler('logs/app.log')
file_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logging.getLogger("uvicorn.access").disabled = True
