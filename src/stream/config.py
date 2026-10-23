"""
Streaming configuration.

Defaults are intentionally conservative so the client remains usable on
older CPUs, integrated graphics, and low-power devices.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class VideoCodec(Enum):
    H264 = "h264"
    H265 = "hevc"


class DecodeMode(Enum):
    SOFTWARE = "software"          # Always available, preferred for compatibility
    HARDWARE = "hardware"          # Optional acceleration when present
    AUTO = "auto"                  # Prefer software on weak hardware


@dataclass
class StreamConfig:
    # Resolution caps (older hardware)
    max_width: int = 1280
    max_height: int = 720
    target_fps: int = 30

    # Bitrate (kbps) – keep modest by default
    max_bitrate_kbps: int = 8000
    min_bitrate_kbps: int = 2000

    # Codec preference
    preferred_codec: VideoCodec = VideoCodec.H264   # H.264 is more widely software-decodable

    # Decode path
    decode_mode: DecodeMode = DecodeMode.SOFTWARE

    # Latency / quality trade-offs
    enable_frame_dropping: bool = True
    max_queued_frames: int = 3          # Keep pipeline short for older machines

    # Audio
    audio_sample_rate: int = 48000
    audio_channels: int = 2

    # Network
    receive_buffer_size: int = 2 * 1024 * 1024   # 2 MiB

    # Debugging / development
    dump_raw_packets: bool = False
    log_stats_interval_sec: float = 5.0

    def is_low_power(self) -> bool:
        """Heuristic used by the pipeline to decide aggressive settings."""
        return (
            self.max_width <= 1280
            and self.target_fps <= 30
            and self.decode_mode in (DecodeMode.SOFTWARE, DecodeMode.AUTO)
        )
