from src.client import IRCClient


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

    def _handle_ping(self):
        raise NotImplemented

    def _handle_who(self):
        raise NotImplemented

    def _handle_welcome(self):
        raise NotImplemented

    def run_forever(self) -> None:
        """
        Starts main bot loop. Loop ends when exit condition is met
        (TODO: determine exit condition)
        """
        pass
