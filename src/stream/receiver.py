"""
Network receiver for the Remote Play media stream.

Listens on a UDP socket (typical for low-latency game streaming) and
hands complete packets to the pipeline.
"""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import Callable, Optional

from .config import StreamConfig

logger = logging.getLogger(__name__)

PacketHandler = Callable[[bytes, tuple], None]


class StreamReceiver:
    """
    Asynchronous UDP receiver tuned for real-time video/audio packets.
    """

    def __init__(self, config: StreamConfig):
        self.config = config
        self._sock: Optional[socket.socket] = None
        self._transport: Optional[asyncio.DatagramTransport] = None
        self._protocol: Optional[asyncio.DatagramProtocol] = None
        self._running = False
        self._packet_handler: Optional[PacketHandler] = None
        self._packets_received = 0
        self._bytes_received = 0

    def set_packet_handler(self, handler: PacketHandler) -> None:
        self._packet_handler = handler

    async def start(self, host: str = "0.0.0.0", port: int = 0) -> int:
        """
        Bind and start receiving.

        Returns the actual bound port (useful when port=0).
        """
        loop = asyncio.get_running_loop()

        # Create a large-buffer UDP socket suitable for high-bitrate streams
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.config.receive_buffer_size)
        sock.bind((host, port))
        sock.setblocking(False)

        self._sock = sock
        bound_port = sock.getsockname()[1]

        class _Protocol(asyncio.DatagramProtocol):
            def __init__(self, outer: "StreamReceiver"):
                self.outer = outer

            def datagram_received(self, data: bytes, addr):
                self.outer._on_datagram(data, addr)

            def error_received(self, exc):
                logger.error("Receiver error: %s", exc)

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: _Protocol(self),
            sock=sock,
        )

        self._transport = transport
        self._protocol = protocol
        self._running = True

        logger.info("Stream receiver listening on %s:%d", host, bound_port)
        return bound_port

    def _on_datagram(self, data: bytes, addr) -> None:
        self._packets_received += 1
        self._bytes_received += len(data)

        if self._packet_handler:
            try:
                self._packet_handler(data, addr)
            except Exception as e:
                logger.exception("Packet handler raised: %s", e)

    async def stop(self) -> None:
        self._running = False
        if self._transport:
            self._transport.close()
            self._transport = None
        if self._sock:
            self._sock.close()
            self._sock = None
        logger.info(
            "Receiver stopped – packets: %d, bytes: %d",
            self._packets_received,
            self._bytes_received,
        )

    @property
    def stats(self) -> dict:
        return {
            "packets": self._packets_received,
            "bytes": self._bytes_received,
            "running": self._running,
        }
