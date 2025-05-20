
class AppException(Exception):
    def __init__(self, message: str, code: str = "app_error", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class MissingQueryParamException(AppException):
    def __init__(self, message: str = "Missing query param"):
        super().__init__(message, code="missing_query_param_error", status_code=422)
