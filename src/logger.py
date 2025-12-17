"""
Module for handling logging related classes and functions

Style guide: when creating initialize function for logger make sure you add
             extra formatter fields in docstring and explain what they do.
             and follow naming convention where each initializer is marked as private
             and starts with initialize keyword e.g _initialize_socket_logger

Other conventions: All loggers created here should have some kind of base parent for example
                   if logger is focusing on specific behavior of bot name of logger should
                   be in following pattern "bot.<loggable_feature>". This also services
                   technical purpose because all children of parent propagate back to
                   parent logger (more information: https://docs.python.org/3/library/logging.html)
"""

import logging


def _initialize_socket_logger() -> logging.Logger:
    """
    Logger for tracking socket trafic.

    extra formatter fields:
        %(trafic_direction): Shows if socket receives (RECEIVED <<<) or sends message (SENT >>>)
    """

    logger = logging.getLogger("bot.socket")

    formatter = logging.Formatter(
        "[%(asctime)s][%(name)s] %(trafic_direction)s %(message)s"
    )

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


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
            # initialization function is can be any kind of function but must return
            # logging.Logger object
            "socket": _initialize_socket_logger()
        }

    def get_logger(self, name: str) -> logging.Logger:
        return self._loggers[name]
