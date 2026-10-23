"""
Local network discovery of PlayStation consoles.

PS4/PS5 consoles announce themselves on the local network. This module
provides a clean, independent discovery interface.

Real packet formats will be filled in as the protocol is fully documented
independently. For now the structure and public API are complete so the
rest of the application can be built against them.
"""

from __future__ import annotations

import asyncio
import logging
import socket
import struct
import time
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

# Common ports observed in Remote Play related traffic (public knowledge)
DISCOVERY_PORT = 987
CONTROL_PORT_DEFAULT = 9295


@dataclass
class ConsoleInfo:
    """Information about a discovered console."""
    name: str
    host: str
    port: int = CONTROL_PORT_DEFAULT
    is_ps5: bool = True
    is_ready: bool = True
    mac_address: Optional[str] = None
    raw_response: Optional[bytes] = None

    def __str__(self) -> str:
        kind = "PS5" if self.is_ps5 else "PS4"
        status = "ready" if self.is_ready else "standby"
        return f"{self.name} ({kind}) @ {self.host}:{self.port} [{status}]"


async def discover_consoles(
    timeout: float = 3.0,
    broadcast_address: str = "255.255.255.255",
) -> List[ConsoleInfo]:
    """
    Send a discovery probe and collect responses.

    Returns a list of ConsoleInfo objects. On networks where no console
    responds (or while the exact probe format is still being refined),
    the list will be empty – callers should also support manual host entry.
    """
    loop = asyncio.get_running_loop()
    consoles: dict[str, ConsoleInfo] = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind(("0.0.0.0", 0))

    # Minimal discovery probe placeholder.
    # Real implementation will use the correct Remote Play search packet.
    probe = b"SRCH * HTTP/1.1\ndevice-discovery-protocol-version:00020020\n"

    try:
        sock.sendto(probe, (broadcast_address, DISCOVERY_PORT))
        logger.debug("Discovery probe sent to %s:%d", broadcast_address, DISCOVERY_PORT)
    except OSError as e:
        logger.warning("Failed to send discovery probe: %s", e)
        sock.close()
        return []

    end_time = time.monotonic() + timeout

    while time.monotonic() < end_time:
        try:
            data, addr = await asyncio.wait_for(
                loop.sock_recvfrom(sock, 4096),
                timeout=max(0.05, end_time - time.monotonic()),
            )
        except (asyncio.TimeoutError, OSError):
            break

        host = addr[0]
        if host in consoles:
            continue

        info = _parse_discovery_response(data, host)
        if info:
            consoles[host] = info
            logger.info("Discovered: %s", info)

    sock.close()
    return list(consoles.values())


def _parse_discovery_response(data: bytes, host: str) -> Optional[ConsoleInfo]:
    """
    Best-effort parse of a discovery response.

    Real responses contain HTTP-like headers. We extract what we can and
    fall back to sensible defaults.
    """
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        return None

    name = "PlayStation"
    is_ps5 = True
    is_ready = True
    port = CONTROL_PORT_DEFAULT

    for line in text.splitlines():
        line = line.strip()
        lower = line.lower()
        if lower.startswith("host-name:"):
            name = line.split(":", 1)[1].strip() or name
        elif lower.startswith("host-type:"):
            host_type = line.split(":", 1)[1].strip().upper()
            is_ps5 = "PS5" in host_type
        elif lower.startswith("status:"):
            status = line.split(":", 1)[1].strip().lower()
            is_ready = status in ("ok", "ready", "standing by") is False
            # "Standby" / "Standing By" means the console can be woken
            if "stand" in status:
                is_ready = False
        elif lower.startswith("host-request-port:"):
            try:
                port = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass

    return ConsoleInfo(
        name=name,
        host=host,
        port=port,
        is_ps5=is_ps5,
        is_ready=is_ready,
        raw_response=data,
    )


def discover_consoles_sync(timeout: float = 3.0) -> List[ConsoleInfo]:
    """Synchronous wrapper for simple scripts / GUI."""
    return asyncio.run(discover_consoles(timeout=timeout))
