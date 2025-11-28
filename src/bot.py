import json
import socket
import time

from dataclasses import dataclass
from functools import wraps
from typing import Callable, Any, Iterator
from src.tracking_socket import TrackingSocket


def require_connection(method: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        if not self.is_connected:
            raise RuntimeError(
                "Bot is not connected to a server. Please connect to a server and try again."
            )

        return method(self, *args, **kwargs)

    return wrapper


@dataclass
class _BotConfig:
    """
    Configuration class for bot. This should mirror fields in config.json
    which should mirror requirements from IRC protocol (https://www.rfc-editor.org/rfc/rfc1459).
    No other configuration should be added there. If other configuration options is needed use
    .env instead or create separate config file

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

    def __init__(self, proxy: bool = False):
        self.config: _BotConfig = _BotConfig.from_json("./config.json")

        self.nick: str = self.config.NICK
        self.server: str = self.config.SERVER
        self.port: int = self.config.PORT
        self.ident: str = self.config.IDENT
        self.realname: str = self.config.REALNAME
        self.chan: list[str] = self.config.CHAN

        if proxy:
            raise NotImplementedError
            # self.proxy_server: str = self.config.PROXY_SERVER
            # self.proxy_port: int = self.config.PROXY_PORT
            # self.socket = socks.socksocket()
            # self.socket.set_proxy(socks.SOCKS5, self.proxy_server, self.proxy_port)

        else:
            self.socket: TrackingSocket = TrackingSocket(
                socket.AF_INET, socket.SOCK_STREAM
            )

        self.is_connected: bool = False
        self.is_credentials_sent: bool = False
        self.reconnect_delays = iter([60, 300, 3600])  # in seconds

    def connect(self):
        """Connects to server specified in config.json"""
        # Handle connection and set NICK and IDENT for bot
        self.socket.connect((self.server, self.port))
        self.is_connected = True

    def send_credentials(self):
        """
        Sends necessary NICK and USER fields to a server.
        More information can be found from IRC protocol (https://www.rfc-editor.org/rfc/rfc1459)
        """
        self.socket.send(f"NICK {self.nick}\r\n".encode())
        self.socket.send(f"USER {self.nick} * * :{self.nick}\r\n".encode())

    def reconnect(self, delay: int = 30):
        """
        Closes the previous socket. Creates new one before trying to reconnect server.
        This should be only called when server closes the connection without giving proper
        ERROR message.

        param delay: int - Specifies how many seconds bot waits after connection is closed
                           before trying to create new socket and connect to a server.
        """

        self.close()
        time.sleep(delay)
        self.socket = TrackingSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        self.send_credentials()

    def close(self):
        """Closes the bot socket and updates connection status"""
        self.socket.close()
        self.is_connected = False

    @require_connection
    def pong(self, answer):
        """Send pong to a server"""
        self.socket.send(f"PONG :{answer}\r\n".encode())

    @require_connection
    def send_msg(self):
        """Sends message to the channel. Only works after bot has joined to a channel"""
        pass

    @require_connection
    def change_topic(self):
        """
        Changes channel topic. Requires bot to have permissions to do so
        and bot must be connected to a server.
        """
        pass

    @require_connection
    def join_channel(self):
        """Joins channel specified in config.json"""
        for chan in self.chan:
            self.socket.send(f"JOIN :{chan}\r\n".encode())

    @require_connection
    def receive_message(self):
        msg = self.socket.recv(2040)
        return msg.decode()
