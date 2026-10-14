"""DHCP address reservations (fixed IPs) handed out by the gateway."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_int, get_str
from ._utils import normalize_mac


@dataclass(frozen=True)
class AddressReservation:
    """A fixed IPv4 address the DHCP server always leases to ``mac``."""

    mac: str
    ip: str

    @classmethod
    def from_api(cls, data: JsonObject) -> AddressReservation:
        """Build ``AddressReservation`` from a router payload."""
        return cls(mac=normalize_mac(get_str(data, "mac")), ip=get_str(data, "ip"))


@dataclass(frozen=True)
class AddressReservationTable:
    """Every configured reservation plus the maximum the router accepts."""

    reservations: tuple[AddressReservation, ...]
    max_count: int

    @classmethod
    def from_api(cls, data: JsonObject) -> AddressReservationTable:
        """Build ``AddressReservationTable`` from the ``addr_reservation`` getlist result."""
        items = data.get("reservation_list")
        entries = items if isinstance(items, list) else []
        return cls(
            reservations=tuple(
                AddressReservation.from_api(item) for item in entries if isinstance(item, dict)
            ),
            max_count=get_int(data, "reservation_list_max_count"),
        )
