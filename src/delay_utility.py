import threading
import sys
import copy
from typing import Iterator


class ReconnectDelayUtility:
    """
    Utility class for managing the reconnection delays.
    Has internal timer which starts when first delay is obtained. Timer resets after 2h.
    If 3 tries of reconnection have been tried within those 2h. Program exits with sys.exit(1) i.e
    program assumes that if 3 consecutive tries fail failure is critical and would need someone to look into it.
    """

    def __init__(
        self, delays: list[int] | None = None, reset_window: int | None = None
    ):
        self._delays: list[int] = [60, 300, 3600]
        self._reset_window: int = 7200

        if delays is not None:
            self._delays = copy.copy(delays)

        if reset_window is not None:
            self._reset_window = reset_window

        self._delay_iterator: Iterator[int] = iter(self._delays)
        self.retry_attempts = 0

    def _start_timer(self):
        pass

    def _reset_delay(self):
        pass

    def get_delay(self) -> int:
        return next(self._delay_iterator, -1)
