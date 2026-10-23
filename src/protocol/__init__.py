"""
Independent Remote Play protocol layer.

Contains discovery, registration, session handshake and control channel
logic. This is an original implementation and does not derive from Chiaki
or any other existing client.
"""

from .discovery import ConsoleInfo, discover_consoles
from .registration import RegistrationResult, register_console
from .session import RemotePlaySession, SessionState

__all__ = [
    "ConsoleInfo",
    "discover_consoles",
    "RegistrationResult",
    "register_console",
    "RemotePlaySession",
    "SessionState",
]
