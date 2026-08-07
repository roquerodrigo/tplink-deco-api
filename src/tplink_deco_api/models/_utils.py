"""Small shared helpers for decoding router payload fields."""

from __future__ import annotations

from base64 import b64decode

from ..exceptions.base import DecoError


def decode_b64(value: str) -> str:
    """Return the base64-decoded UTF-8 string, or ``value`` if empty.

    Raises :class:`DecoError` when the router sends a field that is not
    valid base64 or does not decode to UTF-8, so callers only ever see the
    SDK exception hierarchy.
    """
    if not value:
        return value
    try:
        return b64decode(value).decode()
    except ValueError as exc:
        raise DecoError(f"Failed to decode base64 field: {exc}") from exc


def normalize_mac(value: str) -> str:
    """Return ``value`` with hyphens converted to colons and uppercased."""
    return value.replace("-", ":").upper()
