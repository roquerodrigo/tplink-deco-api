"""DHCP address reservations: the fixed IP the gateway leases to a client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import AddressReservation, AddressReservationTable
from ._request import require_ipv4, require_mac

if TYPE_CHECKING:
    from .._json import JsonValue
    from ._request import RequestSender

_PATH = "admin/client"
_FORM = "addr_reservation"


class AddressReservationService:
    """Lists, creates, changes and deletes fixed IP reservations."""

    def __init__(self, send: RequestSender) -> None:
        self._send = send

    def get_table(self) -> AddressReservationTable:
        """Return every reservation and the maximum the router accepts."""
        return AddressReservationTable.from_api(self._send(_PATH, _FORM, {"operation": "getlist"}))

    def add(self, reservation: AddressReservation) -> None:
        """Reserve ``reservation.ip`` for ``reservation.mac``."""
        entries: list[JsonValue] = [_to_wire(reservation)]
        self._send(_PATH, _FORM, {"operation": "add", "params": {"reservation_list": entries}})

    def modify(self, current: AddressReservation, replacement: AddressReservation) -> None:
        """Replace the existing ``current`` reservation with ``replacement``."""
        original = _to_wire(current)
        params: dict[str, JsonValue] = {
            **_to_wire(replacement),
            "original_mac": original["mac"],
            "original_ip": original["ip"],
        }
        self._send(_PATH, _FORM, {"operation": "modify", "params": params})

    def remove(self, mac: str) -> None:
        """Drop the reservation held by ``mac``."""
        macs: list[JsonValue] = [require_mac(mac)]
        self._send(_PATH, _FORM, {"operation": "remove", "params": {"reservation_list": macs}})


def _to_wire(reservation: AddressReservation) -> dict[str, JsonValue]:
    return {"mac": require_mac(reservation.mac), "ip": require_ipv4(reservation.ip)}
