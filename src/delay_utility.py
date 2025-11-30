import threading
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
        self._reset_window: int = 7200  # in seconds

        if delays is not None:
            self._delays: list[int] = copy.copy(delays)

        if reset_window is not None:
            self._reset_window: int = reset_window

        self._delay_iterator: Iterator[int] = iter(self._delays)
        self.retry_attempts: int = 0
        self.timer_thread: threading.Timer | None = None

    def _start_timer(self):
        if self.timer_thread:
            self.timer_thread.cancel()

        self.timer_thread = threading.Timer(self._reset_window, self._reset_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def _reset_timer(self):
        self._delay_iterator = iter(self._delays)
        self.retry_attempts = 0
        print("Reconnect timer is reseted")

    def stop_timer(self):
        """
        Stops the timer. This must be called before program exits to guarantee graceful exit
        on shutdown. Program will still halt if critical error happens in main thread but this guarantees
        that thread exits as intended.

        """
        if self.timer_thread:
            self.timer_thread.cancel()

    def get_next_delay(self) -> int:
        """
        Obtain next delay from self._delay_iterator. Additionally starts internal
        timer to keep track of when reconnection delays should reset. If self._delay_iterator is completely
        exhausted returns -1 to indicate reconnection failure.
        """

        self._start_timer()
        return next(self._delay_iterator, -1)
