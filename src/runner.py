from collections.abc import Callable
from src.client import IRCClient

from functools import wraps
from typing import ParamSpec, TypeVar

T = TypeVar("T", covariant=True)
P = ParamSpec("P")


def _on_response(target_response_code: str):
    """
    Decorator factory responsible of constructing decorators
    which can be hooked into a arbittuary event (for irc specific numerics/events check RFC2812)
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
            response_code: str = _MessageParser.get_response_code(args[1])
            if response_code == target_response_code:
                return func(*args, **kwargs)

            return None

        return func_wrapper

    return decor_wrapper


class _MessageParser:
    @staticmethod
    def get_response_code(msg: str):
        raise NotImplemented

    def parse_lines(self, msg: bytes):
        raise NotImplemented


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

    @_on_response("PING")
    def _handle_ping(self, msg: str) -> None:
        # TODO: Parse answer from msg

        answer: str = ""
        self.client.pong(answer)

    @_on_response("352")  # numeric of WHO is 352
    def _handle_who(self, msg: str) -> None:
        raise NotImplemented

    @_on_response("001")  # numeric of Welcome is 001
    def _handle_welcome(self, msg: str) -> None:
        raise NotImplemented

    def run_forever(self, msg: str) -> None:
        """
        Starts main bot loop. Loop ends when exit condition is met
        (TODO: determine exit condition)
        """

        tmp = ""
        self._handle_ping(tmp)
        self._handle_welcome(tmp)
        self._handle_who(tmp)
