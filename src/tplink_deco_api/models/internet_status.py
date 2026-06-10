"""Internet connection status for IPv4 and IPv6."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_int, get_object, get_str


@dataclass(frozen=True)
class IpStatus:
    """Connection state for one IP version (v4 or v6)."""

    inet_status: str
    dial_status: str
    connect_type: str
    auto_detect_type: str
    error_code: int

    @classmethod
    def from_api(cls, data: JsonObject) -> IpStatus:
        """Build ``IpStatus`` from a router payload."""
        return cls(
            inet_status=get_str(data, "inet_status"),
            dial_status=get_str(data, "dial_status"),
            connect_type=get_str(data, "connect_type"),
            auto_detect_type=get_str(data, "auto_detect_type"),
            error_code=get_int(data, "error_code"),
        )


@dataclass(frozen=True)
class InternetStatus:
    """WAN connection status including IPv4, IPv6 and physical link state."""

    ipv4: IpStatus
    ipv6: IpStatus
    link_status: str

    @classmethod
    def from_api(cls, data: JsonObject) -> InternetStatus:
        """Build ``InternetStatus`` from a router payload."""
        return cls(
            ipv4=IpStatus.from_api(get_object(data, "ipv4")),
            ipv6=IpStatus.from_api(get_object(data, "ipv6")),
            link_status=get_str(data, "link_status"),
        )
