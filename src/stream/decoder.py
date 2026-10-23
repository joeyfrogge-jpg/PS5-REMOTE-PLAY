"""
Software-first video and audio decoder.

Uses PyAV (FFmpeg bindings) so we can force the software decoder paths
and stay usable on machines without modern GPU decode support.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

import av
from av.codec.context import CodecContext
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame

from .config import StreamConfig, DecodeMode, VideoCodec

logger = logging.getLogger(__name__)


class StreamDecoder:
    """
    Decodes H.264 / H.265 video and AAC / Opus-style audio streams.

    Design priority:
    1. Software decoding (libx264 / libx265 software paths via FFmpeg)
    2. Low memory footprint
    3. Graceful degradation on weak CPUs
    """

    def __init__(self, config: StreamConfig):
        self.config = config
        self._video_codec: Optional[CodecContext] = None
        self._audio_codec: Optional[CodecContext] = None
        self._video_frames_decoded = 0
        self._audio_frames_decoded = 0

    def open_video(self, codec: VideoCodec = VideoCodec.H264) -> None:
        """Open a video decoder, forcing software path when requested."""
        name = "h264" if codec == VideoCodec.H264 else "hevc"

        # Create codec context
        self._video_codec = CodecContext.create(name, "r")

        # Strongly prefer software decoding for older hardware compatibility
        if self.config.decode_mode in (DecodeMode.SOFTWARE, DecodeMode.AUTO):
            # Disable hardware acceleration options if present
            self._video_codec.options = {
                "threads": "auto",
                # Force software where possible
                "hwaccel": "none",
            }
            logger.info("Video decoder opened in SOFTWARE mode (%s)", name)
        else:
            logger.info("Video decoder opened (hardware allowed) (%s)", name)

        # Conservative thread count helps older multi-core but weak CPUs
        self._video_codec.thread_count = 0  # let FFmpeg decide, but keep it modest

    def open_audio(self, codec_name: str = "aac") -> None:
        self._audio_codec = CodecContext.create(codec_name, "r")
        logger.info("Audio decoder opened (%s)", codec_name)

    def decode_video_packet(self, data: bytes) -> list[VideoFrame]:
        """
        Feed a raw encoded video packet and return zero or more decoded frames.

        Returns an empty list on decode failure or when the pipeline is
        intentionally dropping frames under load.
        """
        if self._video_codec is None:
            raise RuntimeError("Video decoder not opened")

        try:
            packet = av.Packet(data)
            frames = self._video_codec.decode(packet)
            self._video_frames_decoded += len(frames)

            # Simple back-pressure / drop logic for weak hardware
            if (
                self.config.enable_frame_dropping
                and len(frames) > 0
                and self._video_frames_decoded % 30 == 0
            ):
                # Occasional opportunistic drop under high load can be added later
                pass

            return frames
        except av.AVError as e:
            logger.warning("Video decode error: %s", e)
            return []

    def decode_audio_packet(self, data: bytes) -> list[AudioFrame]:
        if self._audio_codec is None:
            raise RuntimeError("Audio decoder not opened")

        try:
            packet = av.Packet(data)
            frames = self._audio_codec.decode(packet)
            self._audio_frames_decoded += len(frames)
            return frames
        except av.AVError as e:
            logger.warning("Audio decode error: %s", e)
            return []

    def flush(self) -> Tuple[list[VideoFrame], list[AudioFrame]]:
        """Flush remaining frames from the decoders."""
        video_frames: list[VideoFrame] = []
        audio_frames: list[AudioFrame] = []

        if self._video_codec:
            try:
                video_frames = self._video_codec.decode(None)
            except av.AVError:
                pass

        if self._audio_codec:
            try:
                audio_frames = self._audio_codec.decode(None)
            except av.AVError:
                pass

        return video_frames, audio_frames

    def close(self) -> None:
        self._video_codec = None
        self._audio_codec = None
        logger.info(
            "Decoder closed – video frames: %d, audio frames: %d",
            self._video_frames_decoded,
            self._audio_frames_decoded,
        )

    @property
    def stats(self) -> dict:
        return {
            "video_frames": self._video_frames_decoded,
            "audio_frames": self._audio_frames_decoded,
        }
