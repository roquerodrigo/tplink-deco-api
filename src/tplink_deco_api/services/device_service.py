"""Actions on the Deco nodes themselves."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._request import require_mac

if TYPE_CHECKING:
    from .._json import JsonValue
    from ._request import RequestSender


class DeviceService:
    """Reboots the mesh nodes listed by :meth:`DecoClient.get_device_list`."""

    def __init__(self, send: RequestSender) -> None:
        self._send = send

    def reboot(self, *macs: str) -> None:
        """Reboot the nodes whose MACs are given.

        Rebooting the gateway drops the session and the internet connection
        until it is back up.
        """
        if not macs:
            message = "Failed to reboot: pass at least one node MAC"
            raise ValueError(message)
        mac_list: list[JsonValue] = [{"mac": require_mac(mac)} for mac in macs]
        self._send(
            "admin/device", "system", {"operation": "reboot", "params": {"mac_list": mac_list}}
        )
