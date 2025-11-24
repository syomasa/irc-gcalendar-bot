import json
import socket
from dataclasses import dataclass
from dotenv import dotenv_values
from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec


def require_connection(method: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(method)
    def wrapper(self: IRCBot, *args, **kwargs) -> Any:
        if self.socket is None:
            raise RuntimeError(
                "Bot is not connected to a server. Please connect to a server and try again."
            )

        return method(self, *args, **kwargs)

    return wrapper


@dataclass
class _BotConfig:
    """
    Configuration class for bot this should mirror fields in config.json
    which should mirror requirements from IRC specification. No other configuration should be added there.
    If other configuration options is needed use .env instead or create separate config file

    NOTE: Dataclass fields here should follow ALL_CAPS convention when they are directly related to IRC specification
          Otherwise please refrain from using ALL_CAPS or set it as class level variable. Only exception to this is CHAN
          which is defined as list of strings instead of just string,
          because this makes it simpler to manage joining to multiple channels
    """

    NICK: str
    SERVER: str
    PORT: int
    IDENT: str
    REALNAME: str
    CHAN: list[str]
    PROXY_SERVER: str
    PROXY_PORT: int

    @classmethod
    def from_json(cls, path: str):
        with open(path, "r") as fp:
            data = json.load(fp)

        return cls(**data)


class IRCBot:
    """
    Handles all common IRC operations such connection to a server,
    joining to channels, sending messages and changing channel topics
    """

    _socket: socket.socket | None
    socket_connected: socket.socket

    def __init__(self, proxy: bool = False):
        self.config: _BotConfig = _BotConfig.from_json("./config")

        self.nick: str = self.config.NICK
        self.server: str = self.config.SERVER
        self.port: int = self.config.PORT
        self.ident: str = self.config.IDENT
        self.realname: str = self.config.REALNAME
        self.chan: list[str] = self.config.CHAN

        if proxy:
            self.proxy_server: str = self.config.PROXY_SERVER
            self.proxy_port: int = self.config.PROXY_PORT

        self.socket = None
        self._socket = None

    def connect(self):
        """Connects to server specified in config"""

        if self.socket is None:
            self.socket = socket.socket()

        # Handle connection and set NICK and IDENT for bot
        self.socket.connect((self.server, self.port))
        self.socket.send(f"NICK {self.nick}".encode())
        self.socket.send(
            f"USER {self.ident} {self.server} bla :{self.realname}\r\n".encode()
        )

    @require_connection
    def send_msg(self):
        """Sends message to the channel. Only works after bot has joined to a channel"""
        pass

    @require_connection
    def change_topic(self):
        """Changes channel topic. Requires bot to have permissions to do so"""
        pass

    @require_connection
    def join_channel(self):
        """Joins channel specified in .env"""

        for chan in self.chan:
            self.socket.send(f"JOIN :{chan}\r\n".encode())

    @require_connection
    def receive_message(self):
        self.socket.recv(2040)
