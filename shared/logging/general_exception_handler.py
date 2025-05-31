from rest_framework.views import exception_handler

from shared.logging.logger import AppLogger
from utils.logger_helpers import generate_exception_response

logger = AppLogger()


def general_exception_handler(exception, context):
    response = exception_handler(exception, context)

    request = context.get("request", None)

    logger.log_exception(
        feature="DRFExceptionHandler",
        message="Unhandled exception",
        exception=exception,
        path=getattr(request, "path", None),
        request_id=request.headers.get("X-Request-ID") if request else None,
    )

    if response is None:
        return generate_exception_response()

    return response
