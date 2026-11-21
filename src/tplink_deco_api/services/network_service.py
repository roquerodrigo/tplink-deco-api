"""LAN addressing of the Deco nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import LanIp
from ._request import require_ipv4, require_netmask

if TYPE_CHECKING:
    from .._json import JsonValue
    from ._request import RequestSender

_PATH = "admin/network"
_LAN_IP_FORM = "lan_ip"


class NetworkService:
    """Reads and changes the LAN IP address of a node."""

    def __init__(self, send: RequestSender) -> None:
        self._send = send

    def get_lan_ip(self, device_mac: str = "default") -> LanIp:
        """Return the LAN IPv4 address and mask of ``device_mac``.

        The firmware answers HTTP 500 when no node is named, so ``"default"``
        is always sent unless a node MAC is given.
        """
        result = self._send(
            _PATH, _LAN_IP_FORM, {"operation": "read", "params": {"device_mac": device_mac}}
        )
        return LanIp.from_api(result)

    def set_lan_ip(self, ip: str, mask: str, device_mac: str = "default") -> None:
        """Move ``device_mac`` to ``ip`` / ``mask``.

        The router stops answering on its old address, so the current session
        is lost: open a new :class:`~tplink_deco_api.DecoClient` on ``ip``.
        """
        params: dict[str, JsonValue] = {
            "device_mac": device_mac,
            "lan_ip": {"ip": require_ipv4(ip), "mask": require_netmask(mask)},
        }
        self._send(_PATH, _LAN_IP_FORM, {"operation": "write", "params": params})
