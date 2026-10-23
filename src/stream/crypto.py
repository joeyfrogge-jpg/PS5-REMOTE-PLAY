"""
Stream encryption / decryption helpers.

PlayStation Remote Play streams are encrypted. This module provides a clean
interface so the rest of the pipeline does not care about the exact cipher.

The real key material and IV handling will be filled in once the session
handshake is fully implemented. For now this is a well-defined placeholder
that can accept a session key.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class StreamCrypto:
    """
    Handles decryption of incoming video / audio packets.

    Expected real-world implementation will use AES (likely GCM or CTR)
    with keys derived during the Remote Play session handshake.
    """

    def __init__(self):
        self._session_key: Optional[bytes] = None
        self._ready = False

    def set_session_key(self, key: bytes) -> None:
        """
        Install the key material obtained from the control / handshake layer.
        """
        if len(key) not in (16, 24, 32):
            raise ValueError("Session key must be 128, 192 or 256 bits")
        self._session_key = key
        self._ready = True
        logger.info("Stream crypto key installed (%d bits)", len(key) * 8)

    def decrypt(self, ciphertext: bytes, associated_data: bytes = b"") -> bytes:
        """
        Decrypt a single packet.

        Currently a pass-through so the pipeline can be developed end-to-end.
        Replace with real AES-GCM / AES-CTR once keys are available.
        """
        if not self._ready:
            # During early development we allow cleartext testing
            return ciphertext

        # TODO: real implementation
        # from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        # ...
        logger.debug("Decrypting %d bytes (placeholder)", len(ciphertext))
        return ciphertext

    def is_ready(self) -> bool:
        return self._ready
