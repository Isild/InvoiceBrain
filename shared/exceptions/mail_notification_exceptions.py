

class NotificationMailMissingFieldException(Exception):
    def __init__(self, message: str, *, feature: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.feature = feature
        self.details = details or {}
