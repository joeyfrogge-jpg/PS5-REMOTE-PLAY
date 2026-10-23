"""
Utilities for handling the PSN Account ID in the format expected by Remote Play.
"""

import base64
from typing import Union


def account_id_to_base64(account_id: Union[int, str]) -> str:
    """
    Convert a numeric PSN Account ID to the 8-byte little-endian base64 string
    used for console registration.
    """
    if isinstance(account_id, str):
        account_id = int(account_id)

    # Must be exactly 8 bytes, little-endian
    raw = account_id.to_bytes(8, byteorder="little", signed=False)
    return base64.b64encode(raw).decode("ascii")


def base64_to_account_id(b64: str) -> int:
    """
    Convert a base64 Account ID string back to the numeric value.
    """
    raw = base64.b64decode(b64)
    if len(raw) != 8:
        raise ValueError("Account ID base64 must decode to exactly 8 bytes")
    return int.from_bytes(raw, byteorder="little", signed=False)
