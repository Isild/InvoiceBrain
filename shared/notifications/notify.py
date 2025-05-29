from abc import ABC, abstractmethod
from shared.logging.logger import AppLogger


class Notify(ABC):
    _valid_message_fields: list[str] = []
    logger = AppLogger()

    @abstractmethod
    def _get_valid_message_fields(self, fields_to_check: dict[str, str]) -> dict[str, str]:
        pass

    @abstractmethod
    def _generate_message(self, message_data: dict[str, str]) -> str:
        pass

    @abstractmethod
    def send(self, mails: list[str], subject: str, message_data: dict[str, str]) -> None:
        pass
