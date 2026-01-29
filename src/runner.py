from collections.abc import Callable
from src.client import IRCClient

from functools import wraps
from typing import ParamSpec, TypeVar, Generator

T = TypeVar("T", covariant=True)
P = ParamSpec("P")


def _on_ping(func: Callable[P, T]) -> Callable[P, T | None]:
    @wraps(func)
    def _wrapper(*args: P.args, **kwargs: P.kwargs):
        # Similarily to _on_response requires two args args[0] instance (self) and msg (str)
        if len(args) < 2:
            return None

        if not isinstance(args[1], str):
            raise TypeError(
                f"Args[1] is expected to be string but got {type(args[1])} instead"
            )

        if args[1].startswith("PING"):
            return func(*args, **kwargs)

        return None

    return _wrapper


def _on_response(target_response_code: str):
    """
    Decorator factory responsible of constructing decorators
    which can be hooked into a arbittuary event (for irc specific numerics/events check RFC2812)

    NOTE: This can be used with any normal message from server except PING.
          Handle ping with its own decorator (@_on_ping)
    """

    def decor_wrapper(func: Callable[P, T]) -> Callable[P, T | None]:
        @wraps(func)
        def func_wrapper(*args: P.args, **kwargs: P.kwargs):
            # Ensure that there is two arguments instance (self) and msg (str)
            # this decorator expects these two to exist to work properly.
            if len(args) < 2:
                return None

            # This decorator assumes that msg (args[1]) is decoded before (i.e type(args[1]) == str)
            # handed over to parser, don't change unless absolutely necessary
            if not isinstance(args[1], str):
                raise TypeError(
                    f"Args[1] is expected to be string but got {type(args[1])} instead"
                )

            msg: str = args[1]
            response_code: str = _MessageParser.get_response_code(msg)
            if response_code == target_response_code:
                return func(*args, **kwargs)

            return None

        return func_wrapper

    return decor_wrapper


class _MessageParser:
    @staticmethod
    def get_response_code(msg: str) -> str:
        msg = msg.strip()
        if not msg.startswith(":"):
            return ""

        parts = msg.split(" ", maxsplit=2)
        return parts[1] if len(parts) > 1 else ""

    @staticmethod
    def parse_lines(msg: bytes) -> Generator[str, str, None]:
        msg_decoded: str = msg.decode("utf-8")

        for line in msg_decoded.split("\r\n"):
            yield line


class BotRunner:
    """
    Simple class responsible for handling runtime logic and
    making calling IRCClient methods

    Runner works on principle of state machine where state is based on response code
    obtained from IRCClient's socket

    Style guide: if bot must handle some response from server or update state based event from socket
                 response it is advised to construct separate handler
                 for it with prefix handle_<response>
    """

    def __init__(self, client: IRCClient):
        self.client = client

    def _initialize_connection(self):
        self.client.connect()
        self.client.send_credentials()

    @_on_ping
    def _handle_ping(self, msg: str) -> None:
        """
        Handles answering to PING messages from server.

        NOTE: to register this don't use @_on_response(...) it is meant to handle standard messages
              with format <prefix> <command> <params> but ping format uses "PING <server_id>"
              format instead. Use @_on_ping decorator instead
        """

        server_id = msg.split(":")[1]
        self.client.pong(server_id)

    @_on_response("352")  # numeric of WHO is 352
    def _handle_who(self, msg: str) -> None:
        print("WHO received")

    @_on_response("001")  # numeric of Welcome is 001
    def _handle_welcome(self, msg: str) -> None:
        print("WELCOME received")

    def run_forever(self) -> None:
        """
        Starts main bot loop. Loop ends when exit condition is met
        (TODO: determine exit condition)
        """

        self._initialize_connection()

        while True:
            raw_msg: bytes = self.client.receive_message()
            msg: str = raw_msg.decode(encoding="utf-8")

            if not msg:
                self.client.reconnect()

            for line in _MessageParser.parse_lines(raw_msg):
                self._handle_ping(line)
                self._handle_welcome(line)
                self._handle_who(line)
