"""Shared plumbing for the services that issue authenticated requests."""

from __future__ import annotations

import ipaddress
import re
from typing import TYPE_CHECKING

from ..models._utils import to_router_mac

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from .._json import JsonObject, JsonValue

type RequestSender = Callable[[str, str, Mapping[str, JsonValue]], JsonObject]
type RawRequestSender = Callable[[str, str, Mapping[str, JsonValue]], JsonValue]

_MAC_PATTERN: re.Pattern[str] = re.compile(r"[0-9A-Fa-f]{2}([:-][0-9A-Fa-f]{2}){5}")


def require_mac(value: str) -> str:
    """Return ``value`` in the router's MAC wire format, rejecting malformed input."""
    if not _MAC_PATTERN.fullmatch(value):
        message = f"Failed to parse MAC address: {value!r} is not six hex octets"
        raise ValueError(message)
    return to_router_mac(value)


def require_ipv4(value: str) -> str:
    """Return ``value`` unchanged when it is a dotted IPv4 address."""
    try:
        ipaddress.IPv4Address(value)
    except ValueError as exc:
        message = f"Failed to parse IPv4 address: {value!r}"
        raise ValueError(message) from exc
    return value


def require_netmask(value: str) -> str:
    """Return ``value`` unchanged when it is a dotted IPv4 netmask such as ``255.255.255.0``."""
    try:
        netmask = str(ipaddress.IPv4Network(f"0.0.0.0/{value}").netmask)
    except ValueError:
        netmask = ""
    if netmask != value:
        message = f"Failed to parse IPv4 netmask: {value!r}"
        raise ValueError(message)
    return value
