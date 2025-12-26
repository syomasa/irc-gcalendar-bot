import socket
import logging

from typing import Literal, TypeAlias
from collections.abc import Buffer
from src.logger import LoggerManager

# This can also be found from _typeshed module but just to prevent potential changes
# to type defined there we define it here instead. This way we can guarantee that ReadableBuffer
# refers indeed Buffer type. If you later on want to change the definition please refer
# to https://github.com/python/typeshed/tree/main/stdlib/_typeshed
# and https://github.com/python/typeshed/blob/main/stdlib/_typeshed/__init__.pyi
ReadableBuffer: TypeAlias = Buffer


def _first_n_bytes(payload: ReadableBuffer, n: int) -> bytes:
    """
    Helper function which returns n bytes from payload.
    This should work on any object which implements Buffer protocol
    """

    view = memoryview(payload)
    return bytes(view[:n])


class TrackingSocket(socket.socket):
    """Adds monitoring and tracking of outgoing messages sent by socket"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._supress_send_logging: bool = False
        self._socket_logger: logging.Logger = LoggerManager().get_logger("socket")

    def _log_traffic(
        self,
        payload: ReadableBuffer,
        traffic: Literal["in", "out"],
        *,
        truncate: int = 512,
        decode=False,
    ) -> None:
        chunk: bytes = _first_n_bytes(payload, truncate)
        if decode:
            try:
                msg = chunk.decode("utf-8", errors="replace")
            except UnicodeDecodeError as e:
                msg = repr(chunk)
                self._socket_logger.warning(
                    "Warning!: Decode failed, falling back to repr", f"Error: {e}"
                )
        else:
            msg = repr(chunk)

        if traffic == "in":
            self._socket_logger.info(msg, extra={"traffic_direction": "RECEIVED <<"})
        elif traffic == "out":
            self._socket_logger.info(msg, extra={"traffic_direction": "SENT >>"})

    def send(
        self,
        data: ReadableBuffer,
        flags: int = 0,
        /,
        *,
        logging_decode: bool = False,
    ) -> int:
        if not self._supress_send_logging:
            self._log_traffic(data, "out", decode=logging_decode)
        return super().send(data, flags)

    def sendall(
        self, data: ReadableBuffer, flags: int = 0, /, *, logging_decode: bool = False
    ) -> None:
        self._supress_send_logging = True
        self._log_traffic(data, "out", decode=logging_decode)
        try:
            super().sendall(data, flags)
        finally:
            self._supress_send_logging = False
