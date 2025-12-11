import socket
import logging


class TrackingSocket(socket.socket):
    """Adds monitoring and tracking of outgoing messages sent by socket"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger: logging.Logger = logging.getLogger("irc-bot")

    def send(self, data, *args, **kwargs):
        chunk = data[:512]
        try:
            chunk = chunk.decode("utf-8", errors="replace")
        except Exception as e:
            chunk = repr(chunk)
            self._logger.warning(
                "Warning!: Decode failed, falling back to repr", f"Error: {e}"
            )

        self._logger.info(f"SENT >> {chunk}")
        return super().send(data, *args, **kwargs)
