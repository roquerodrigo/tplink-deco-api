"""WAN and LAN IP configuration for a Deco node."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_bool, get_object, get_str
from ._utils import normalize_mac


@dataclass(frozen=True)
class IpInfo:
    """IP address, mask, gateway and DNS for one interface."""

    ip: str
    mask: str
    mac: str
    gateway: str
    dns1: str
    dns2: str

    @classmethod
    def from_api(cls, data: JsonObject) -> IpInfo:
        """Build ``IpInfo`` from a router payload."""
        return cls(
            ip=get_str(data, "ip"),
            mask=get_str(data, "mask"),
            mac=normalize_mac(get_str(data, "mac")),
            gateway=get_str(data, "gateway"),
            dns1=get_str(data, "dns1"),
            dns2=get_str(data, "dns2"),
        )


@dataclass(frozen=True)
class WanDetails:
    """WAN interface configuration including IP info and dial type."""

    ip_info: IpInfo
    dial_type: str
    enable_auto_dns: bool

    @classmethod
    def from_api(cls, data: JsonObject) -> WanDetails:
        """Build ``WanDetails`` from a router payload."""
        return cls(
            ip_info=IpInfo.from_api(get_object(data, "ip_info")),
            dial_type=get_str(data, "dial_type"),
            enable_auto_dns=get_bool(data, "enable_auto_dns"),
        )


@dataclass(frozen=True)
class LanDetails:
    """LAN interface IP configuration."""

    ip_info: IpInfo

    @classmethod
    def from_api(cls, data: JsonObject) -> LanDetails:
        """Build ``LanDetails`` from a router payload."""
        return cls(ip_info=IpInfo.from_api(get_object(data, "ip_info")))


@dataclass(frozen=True)
class WanInfo:
    """WAN and LAN IP configuration as reported by a Deco node."""

    wan: WanDetails
    lan: LanDetails

    @classmethod
    def from_api(cls, data: JsonObject) -> WanInfo:
        """Build ``WanInfo`` from a router payload."""
        return cls(
            wan=WanDetails.from_api(get_object(data, "wan")),
            lan=LanDetails.from_api(get_object(data, "lan")),
        )
