"""
Streaming pipeline for PS5-REMOTE-PLAY.

Focus: software decoding first, low resource usage, older hardware compatibility.
"""

from .pipeline import StreamPipeline
from .config import StreamConfig

__all__ = ["StreamPipeline", "StreamConfig"]
