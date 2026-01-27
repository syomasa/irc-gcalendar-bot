from collections.abc import Callable
from src.client import IRCClient

from functools import wraps
from typing import ParamSpec, TypeVar

T = TypeVar("T", covariant=True)
P = ParamSpec("P")


def on_response(response_code: str):
    def decor_wrapper(func: Callable[P, T]) -> Callable[P, T | None]:
        @wraps(func)
        def func_wrapper(*args: P.args, **kwargs: P.kwargs):
            if len(args) > 1 and args[1] == response_code:
                return func(*args, **kwargs)

            return None

        return func_wrapper

    return decor_wrapper


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
        self.state = ...

    def _initialize_connection(self):
        self.client.connect()
        self.client.send_credentials()

    def _parse_msg(self):
        pass

    @on_response("PING")
    def _handle_ping(self, msg: str) -> None:
        # TODO: Parse answer from msg

        answer: str = ""
        self.client.pong(answer)

    def _handle_who(self, msg: str) -> None:
        raise NotImplemented

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

    @on_response("001")
    def test_msg(self, msg: str) -> None:
        print(msg)
