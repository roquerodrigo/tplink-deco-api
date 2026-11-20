"""Wireless backhaul status reported by the ``bridge`` form."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_bool, get_str


@dataclass(frozen=True)
class WirelessBridge:
    """Backhaul link state and placement quality of a Deco node."""

    status: str
    location: str
    support_plc: bool

    @classmethod
    def from_api(cls, data: JsonObject) -> WirelessBridge:
        """Build ``WirelessBridge`` from a router payload."""
        return cls(
            status=get_str(data, "status"),
            location=get_str(data, "location"),
            support_plc=get_bool(data, "support_plc"),
        )
