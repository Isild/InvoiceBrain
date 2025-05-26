import logging
import json
import os

from datetime import datetime

class JsonFileFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "feature": getattr(record, "feature", None),
            "message": record.getMessage(),
            "exception_type": getattr(record, "exception_type", None),
            "exception": self.formatException(record.exc_info) if record.exc_info else None,
            "path": getattr(record, "path", None),
            "request_id": getattr(record, "request_id", None),
        }
        return json.dumps(log_record)


class AppLogger:
    def __init__(self):
        os.makedirs("logs", exist_ok=True)

        self.logger = logging.getLogger("app_json_logger")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.FileHandler("logs/app.log")
            handler.setFormatter(JsonFileFormatter())
            self.logger.addHandler(handler)

    def log_exception(self, feature, message, exception=None, path=None, request_id=None):
        extra = {
            "feature": feature,
            "path": path,
            "request_id": request_id,
            "exception_type": type(exception).__name__ if exception else None,
            # "timestamp": "twoj wiesz czo"
        }
        if exception:
            exc_info = (type(exception), exception, exception.__traceback__)
        else:
            exc_info = None
        self.logger.error(message, exc_info=exc_info, extra=extra)

    def log_info(self, feature, message, path=None, request_id=None):
        extra = {
            "feature": feature,
            "path": path,
            "request_id": request_id,
            "log_moj_type": "info"
        }
        self.logger.info(message, extra=extra)
