"""
Remote Play session lifecycle and control channel.

A session ties together:
  - registration / authentication state
  - control channel (commands, resolution, bitrate, input)
  - the media streaming pipeline
"""

from __future__ import annotations

import asyncio
import logging
from enum import Enum, auto
from typing import Optional

from src.stream import StreamPipeline, StreamConfig
from .discovery import ConsoleInfo
from .registration import register_console, RegistrationResult

logger = logging.getLogger(__name__)


class SessionState(Enum):
    IDLE = auto()
    DISCOVERING = auto()
    REGISTERING = auto()
    CONNECTING = auto()
    STREAMING = auto()
    STOPPING = auto()
    ERROR = auto()


class RemotePlaySession:
    """
    High-level session object used by the GUI / application.

    Usage sketch:

        session = RemotePlaySession(account_id_b64="...")
        consoles = await session.discover()
        await session.connect(consoles[0], pin="12345678")
        # streaming is now active via session.pipeline
        await session.stop()
    """

    def __init__(
        self,
        account_id_b64: str,
        stream_config: Optional[StreamConfig] = None,
    ):
        self.account_id_b64 = account_id_b64.strip()
        self.stream_config = stream_config or StreamConfig()
        self.state = SessionState.IDLE
        self.console: Optional[ConsoleInfo] = None
        self.pipeline: Optional[StreamPipeline] = None
        self._control_reader: Optional[asyncio.StreamReader] = None
        self._control_writer: Optional[asyncio.StreamWriter] = None
        self._session_key: Optional[bytes] = None
        self.last_error: Optional[str] = None

    async def discover(self, timeout: float = 3.0):
        from .discovery import discover_consoles

        self.state = SessionState.DISCOVERING
        try:
            consoles = await discover_consoles(timeout=timeout)
            return consoles
        finally:
            if self.state == SessionState.DISCOVERING:
                self.state = SessionState.IDLE

    async def connect(
        self,
        console: ConsoleInfo,
        pin: str,
    ) -> bool:
        """
        Full connect path: register → open control → start media pipeline.

        Returns True on success.
        """
        self.console = console
        self.state = SessionState.REGISTERING
        self.last_error = None

        # 1. Registration
        reg: RegistrationResult = await register_console(
            host=console.host,
            pin=pin,
            account_id_b64=self.account_id_b64,
            port=console.port,
        )

        if not reg.success:
            self.state = SessionState.ERROR
            self.last_error = reg.message
            logger.error("Registration failed: %s", reg.message)
            return False

        self._session_key = reg.session_key
        logger.info("Registration step completed: %s", reg.message)

        # 2. Open control channel (placeholder – real protocol uses a
        #    persistent connection for commands and input)
        self.state = SessionState.CONNECTING
        try:
            self._control_reader, self._control_writer = await asyncio.wait_for(
                asyncio.open_connection(console.host, console.port),
                timeout=8.0,
            )
            logger.info("Control channel opened to %s:%d", console.host, console.port)
        except (OSError, asyncio.TimeoutError) as e:
            self.state = SessionState.ERROR
            self.last_error = f"Control channel failed: {e}"
            logger.error(self.last_error)
            return False

        # 3. Start media pipeline
        self.pipeline = StreamPipeline(self.stream_config)
        if self._session_key:
            self.pipeline.set_session_key(self._session_key)

        try:
            media_port = await self.pipeline.start()
            logger.info("Media pipeline listening on UDP port %d", media_port)

            # In a complete implementation we would now send a "start stream"
            # command on the control channel telling the console which port
            # to send video/audio to, along with desired resolution/bitrate.
            await self._send_start_stream_command(media_port)

        except Exception as e:
            self.state = SessionState.ERROR
            self.last_error = f"Failed to start media pipeline: {e}"
            logger.exception(self.last_error)
            await self._close_control()
            return False

        self.state = SessionState.STREAMING
        logger.info("Session is now STREAMING")
        return True

    async def _send_start_stream_command(self, media_port: int) -> None:
        """
        Tell the console to begin sending the media stream.

        Placeholder – the real command format will be implemented once
        the control protocol is fully documented independently.
        """
        if not self._control_writer:
            return

        # Illustrative only
        cmd = (
            f"STARTSTREAM\r\n"
            f"local-port: {media_port}\r\n"
            f"resolution: {self.stream_config.max_width}x{self.stream_config.max_height}\r\n"
            f"fps: {self.stream_config.target_fps}\r\n"
            f"bitrate: {self.stream_config.max_bitrate_kbps}\r\n"
            f"\r\n"
        ).encode("ascii")

        try:
            self._control_writer.write(cmd)
            await self._control_writer.drain()
            logger.debug("Start-stream command sent (placeholder)")
        except Exception as e:
            logger.warning("Could not send start-stream command: %s", e)

    async def stop(self) -> None:
        if self.state in (SessionState.IDLE, SessionState.STOPPING):
            return

        self.state = SessionState.STOPPING
        logger.info("Stopping session...")

        if self.pipeline and self.pipeline.is_running:
            await self.pipeline.stop()
        self.pipeline = None

        await self._close_control()

        self.state = SessionState.IDLE
        self.console = None
        self._session_key = None
        logger.info("Session stopped")

    async def _close_control(self) -> None:
        if self._control_writer:
            try:
                self._control_writer.close()
                await self._control_writer.wait_closed()
            except Exception:
                pass
            self._control_writer = None
            self._control_reader = None

    @property
    def is_streaming(self) -> bool:
        return self.state == SessionState.STREAMING
