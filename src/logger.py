import logging


def _initialize_socket_logger() -> logging.Logger:
    pass


class LoggerManager:
    """
    Managment utility for handling different loggers.
    Reason for this instead of using logging built-ins dictconfig
    is that this method allows more control, and is easier to work with
    especially when number of services (that need logging) is still unknown
    """

    _instance: "LoggerManager | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self._loggers = {
            # Add name of the logger and its initialization function here
            "socket": _initialize_socket_logger()
        }

    def get_logger(self, name: str) -> logging.Logger:
        return self._loggers[name]
