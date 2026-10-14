"""Small shared helpers for decoding router payload fields."""

from __future__ import annotations

from base64 import b64decode, b64encode

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
        message = f"Failed to decode base64 field: {exc}"
        raise DecoError(message) from exc


def normalize_mac(value: str) -> str:
    """Return ``value`` with hyphens converted to colons and uppercased."""
    return value.replace("-", ":").upper()


def encode_b64(value: str) -> str:
    """Return ``value`` UTF-8 encoded as base64, the wire format for client names."""
    return b64encode(value.encode()).decode()


def to_router_mac(value: str) -> str:
    """Return ``value`` in the router's wire format: uppercase and hyphen-separated."""
    return value.replace(":", "-").upper()
