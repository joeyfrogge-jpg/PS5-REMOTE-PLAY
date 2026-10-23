"""
Console registration using the PSN Account ID (base64).

Registration is the step where the client proves it is allowed to stream
from the console by presenting the Account ID and the PIN shown on the
PlayStation screen.
"""

from __future__ import annotations

import asyncio
import logging
import socket
from dataclasses import dataclass
from typing import Optional

from src.core.account import base64_to_account_id

logger = logging.getLogger(__name__)


@dataclass
class RegistrationResult:
    success: bool
    message: str
    registered_host: Optional[str] = None
    session_key: Optional[bytes] = None  # derived material for later crypto


async def register_console(
    host: str,
    pin: str,
    account_id_b64: str,
    port: int = 9295,
    timeout: float = 10.0,
) -> RegistrationResult:
    """
    Attempt to register this client with the console.

    Parameters
    ----------
    host : str
        IP address of the console.
    pin : str
        8-digit PIN currently displayed on the PlayStation
        (Settings → System → Remote Play → Pair Device).
    account_id_b64 : str
        The 8-byte little-endian base64 PSN Account ID.
    port : int
        Control port (usually obtained from discovery).
    """
    pin = pin.strip()
    if not (pin.isdigit() and len(pin) == 8):
        return RegistrationResult(
            success=False,
            message="PIN must be exactly 8 digits",
        )

    try:
        # Validate the Account ID format early
        account_id = base64_to_account_id(account_id_b64.strip())
    except Exception as e:
        return RegistrationResult(
            success=False,
            message=f"Invalid base64 Account ID: {e}",
        )

    logger.info(
        "Attempting registration with %s:%d (Account ID numeric=%s)",
        host, port, account_id,
    )

    # ------------------------------------------------------------------
    # Protocol note:
    # The real registration exchange is a short TCP (or sometimes UDP)
    # dialogue that sends the Account ID + PIN and receives a success
    # response plus key material.  The exact packet layout is still being
    # independently documented.
    #
    # Below we implement the full public interface and a realistic
    # connection attempt so the rest of the application can be developed
    # against a stable API.  When the packet formats are finalized they
    # will replace the placeholder section.
    # ------------------------------------------------------------------

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
    except (OSError, asyncio.TimeoutError) as e:
        return RegistrationResult(
            success=False,
            message=f"Could not connect to {host}:{port} – {e}",
        )

    try:
        # Placeholder registration request.
        # Real implementation will construct the correct binary / HTTP-like
        # registration message containing the Account ID and PIN.
        request = (
            f"POST /sce/rp/regist HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"User-Agent: PS5-REMOTE-PLAY\r\n"
            f"Connection: close\r\n"
            f"Content-Length: 0\r\n"
            f"RP-Version: 10.0\r\n"          # illustrative
            f"RP-Account-Id: {account_id_b64}\r\n"
            f"RP-Pin: {pin}\r\n"
            f"\r\n"
        ).encode("ascii")

        writer.write(request)
        await writer.drain()

        # Read response (best-effort)
        try:
            data = await asyncio.wait_for(reader.read(4096), timeout=5.0)
        except asyncio.TimeoutError:
            data = b""

        response_text = data.decode("utf-8", errors="replace")
        logger.debug("Registration response (%d bytes): %s", len(data), response_text[:200])

        # Very rough success detection – will be replaced with proper parsing
        if b"200" in data[:32] or b"success" in data.lower() or b"OK" in data[:64]:
            # In a real success path we would extract session / registration keys here
            dummy_key = account_id.to_bytes(8, "little") + pin.encode("ascii")
            return RegistrationResult(
                success=True,
                message="Registration request sent (response parsing still under development)",
                registered_host=host,
                session_key=dummy_key[:16].ljust(16, b"\0"),
            )

        return RegistrationResult(
            success=False,
            message=(
                "Console responded but registration was not confirmed. "
                "Exact protocol parsing is still being completed. "
                f"Raw response length: {len(data)} bytes."
            ),
            registered_host=host,
        )

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


def register_console_sync(
    host: str,
    pin: str,
    account_id_b64: str,
    port: int = 9295,
) -> RegistrationResult:
    """Synchronous helper for the GUI."""
    return asyncio.run(register_console(host, pin, account_id_b64, port))
