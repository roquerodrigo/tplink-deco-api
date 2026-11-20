"""Internet connection status for IPv4 and IPv6."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_int, get_object, get_str
from .mobile_status import MobileStatus


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

    @classmethod
    def from_mobile(cls, mobile: MobileStatus) -> IpStatus:
        """Build the IPv4 ``IpStatus`` that a cellular gateway implies."""
        return cls(
            inet_status=mobile.inet_status,
            dial_status=mobile.dial_status,
            connect_type="",
            auto_detect_type="",
            error_code=0,
        )


@dataclass(frozen=True)
class InternetStatus:
    """WAN connection status including IPv4, IPv6 and physical link state.

    LTE / 5G gateways report a ``mobile_cpe`` block instead of ``ipv4``: it is
    exposed as ``mobile``, and ``ipv4`` is then derived from it so callers that
    only read ``ipv4.inet_status`` keep working. ``mobile`` is ``None`` on
    wired models.
    """

    ipv4: IpStatus
    ipv6: IpStatus
    link_status: str
    mobile: MobileStatus | None = None

    @classmethod
    def from_api(cls, data: JsonObject) -> InternetStatus:
        """Build ``InternetStatus`` from a router payload."""
        mobile_data = get_object(data, "mobile_cpe")
        mobile = MobileStatus.from_api(mobile_data) if mobile_data else None
        ipv4_data = get_object(data, "ipv4")
        if ipv4_data or mobile is None:
            ipv4 = IpStatus.from_api(ipv4_data)
        else:
            ipv4 = IpStatus.from_mobile(mobile)
        return cls(
            ipv4=ipv4,
            ipv6=IpStatus.from_api(get_object(data, "ipv6")),
            link_status=get_str(data, "link_status"),
            mobile=mobile,
        )
