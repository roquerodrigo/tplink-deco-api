"""LAN address of a Deco node as reported by the ``lan_ip`` form."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_object, get_str, get_str_tuple
from ._utils import normalize_mac


@dataclass(frozen=True)
class LanIp:
    """LAN IPv4 address and mask, plus the DNS servers and WAN IPs the node reports."""

    ip: str
    mask: str
    mac: str
    dns_servers: tuple[str, ...]
    wan_ips: tuple[str, ...]

    @classmethod
    def from_api(cls, data: JsonObject) -> LanIp:
        """Build ``LanIp`` from a router payload."""
        lan = get_object(data, "lan_ip")
        return cls(
            ip=get_str(lan, "ip"),
            mask=get_str(lan, "mask"),
            mac=normalize_mac(get_str(data, "mac_addr")),
            dns_servers=get_str_tuple(data, "dns_server_ip"),
            wan_ips=get_str_tuple(data, "wan_ip"),
        )
