import socket
import sys


class TrackingSocket(socket.socket):
    """Adds monitoring and tracking of outgoing messages sent by socket"""

    def send(self, data, *args, **kwargs):
        chunk = data[:512]
        try:
            chunk = chunk.decode("utf-8", errors="replace")
        except Exception as e:
            chunk = repr(chunk)
            sys.stderr.write(f"Warning!: Decode failed, falling back to repr - {e}\n")

        sys.stdout.write(f">> {chunk}\n")
        sys.stdout.flush()

        return super().send(data, *args, **kwargs)
