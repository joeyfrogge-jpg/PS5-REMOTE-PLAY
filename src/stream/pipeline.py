"""
Main streaming pipeline.

Orchestrates:
  network receive → decrypt → demux → software decode → (future: render)

Designed so each stage can be swapped or disabled independently.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Callable, Optional

from .config import StreamConfig, VideoCodec
from .crypto import StreamCrypto
from .decoder import StreamDecoder
from .receiver import StreamReceiver

logger = logging.getLogger(__name__)

# Callback signatures for the UI / renderer layer
VideoFrameCallback = Callable[["av.VideoFrame"], None]
AudioFrameCallback = Callable[["av.AudioFrame"], None]


class StreamPipeline:
    """
    End-to-end media pipeline for a Remote Play session.
    """

    def __init__(self, config: Optional[StreamConfig] = None):
        self.config = config or StreamConfig()
        self.receiver = StreamReceiver(self.config)
        self.crypto = StreamCrypto()
        self.decoder = StreamDecoder(self.config)

        self._video_cb: Optional[VideoFrameCallback] = None
        self._audio_cb: Optional[AudioFrameCallback] = None
        self._running = False
        self._stats_task: Optional[asyncio.Task] = None
        self._start_time = 0.0

        # Very simple demux heuristic for development
        # Real implementation will parse the proprietary header / RTP-like structure
        self._video_payload_type = 0x60
        self._audio_payload_type = 0x61

    def on_video_frame(self, callback: VideoFrameCallback) -> None:
        self._video_cb = callback

    def on_audio_frame(self, callback: AudioFrameCallback) -> None:
        self._audio_cb = callback

    def set_session_key(self, key: bytes) -> None:
        """Called by the session/control layer after handshake."""
        self.crypto.set_session_key(key)

    async def start(self, bind_host: str = "0.0.0.0", bind_port: int = 0) -> int:
        """
        Start the pipeline.

        Returns the UDP port the receiver is listening on so the control
        layer can tell the console where to send the media stream.
        """
        if self._running:
            raise RuntimeError("Pipeline already running")

        # Open decoders early (software path)
        self.decoder.open_video(self.config.preferred_codec)
        self.decoder.open_audio("aac")

        self.receiver.set_packet_handler(self._handle_packet)
        port = await self.receiver.start(bind_host, bind_port)

        self._running = True
        self._start_time = time.monotonic()

        if self.config.log_stats_interval_sec > 0:
            self._stats_task = asyncio.create_task(self._stats_loop())

        logger.info(
            "Stream pipeline started (port %d, max %dx%d @ %dfps, %s decode)",
            port,
            self.config.max_width,
            self.config.max_height,
            self.config.target_fps,
            self.config.decode_mode.value,
        )
        return port

    async def stop(self) -> None:
        self._running = False

        if self._stats_task:
            self._stats_task.cancel()
            try:
                await self._stats_task
            except asyncio.CancelledError:
                pass
            self._stats_task = None

        await self.receiver.stop()
        self.decoder.close()
        logger.info("Stream pipeline stopped")

    def _handle_packet(self, data: bytes, addr) -> None:
        """
        Entry point for every UDP datagram.

        Real protocol parsing will replace the simple header heuristic below.
        """
        if len(data) < 4:
            return

        # Placeholder header parsing (to be replaced with real Remote Play framing)
        # Assume first byte roughly indicates payload type for now
        payload_type = data[0]
        payload = data[1:]  # temporary

        # Decrypt
        try:
            plaintext = self.crypto.decrypt(payload)
        except Exception as e:
            logger.warning("Decrypt failed: %s", e)
            return

        if payload_type == self._video_payload_type or payload_type == 0x00:
            # Treat as video for development
            frames = self.decoder.decode_video_packet(plaintext)
            if self._video_cb:
                for frame in frames:
                    try:
                        self._video_cb(frame)
                    except Exception:
                        logger.exception("Video frame callback error")

        elif payload_type == self._audio_payload_type:
            frames = self.decoder.decode_audio_packet(plaintext)
            if self._audio_cb:
                for frame in frames:
                    try:
                        self._audio_cb(frame)
                    except Exception:
                        logger.exception("Audio frame callback error")

        else:
            # Unknown / control / FEC – ignore for now
            pass

    async def _stats_loop(self) -> None:
        while self._running:
            await asyncio.sleep(self.config.log_stats_interval_sec)
            uptime = time.monotonic() - self._start_time
            rstats = self.receiver.stats
            dstats = self.decoder.stats
            logger.info(
                "[stats] uptime=%.1fs  packets=%d  bytes=%d  "
                "video_frames=%d  audio_frames=%d",
                uptime,
                rstats["packets"],
                rstats["bytes"],
                dstats["video_frames"],
                dstats["audio_frames"],
            )

    @property
    def is_running(self) -> bool:
        return self._running
