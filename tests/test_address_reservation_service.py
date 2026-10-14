"""Unit tests for ``AddressReservationService`` payloads and table parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tplink_deco_api import AddressReservation, AddressReservationService, AddressReservationTable

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tplink_deco_api._json import JsonObject, JsonValue


class _RecordingSender:
    def __init__(self, result: JsonObject | None = None) -> None:
        self.calls: list[tuple[str, str, Mapping[str, JsonValue]]] = []
        self._result: JsonObject = result or {}

    def __call__(self, path: str, form: str, data: Mapping[str, JsonValue]) -> JsonObject:
        self.calls.append((path, form, data))
        return self._result


def test_get_table_parses_reservations_and_limit() -> None:
    sender = _RecordingSender(
        {
            "reservation_list_max_count": 200,
            "reservation_list": [{"mac": "D8-3A-DD-BB-D5-25", "ip": "192.168.5.5"}],
        }
    )
    table = AddressReservationService(sender).get_table()
    assert table == AddressReservationTable(
        reservations=(AddressReservation(mac="D8:3A:DD:BB:D5:25", ip="192.168.5.5"),),
        max_count=200,
    )
    assert sender.calls == [("admin/client", "addr_reservation", {"operation": "getlist"})]


def test_get_table_without_list_is_empty() -> None:
    table = AddressReservationService(_RecordingSender()).get_table()
    assert table == AddressReservationTable(reservations=(), max_count=0)


def test_add_sends_reservation_list() -> None:
    sender = _RecordingSender()
    AddressReservationService(sender).add(AddressReservation("02:00:00:00:00:01", "192.168.5.250"))
    assert sender.calls == [
        (
            "admin/client",
            "addr_reservation",
            {
                "operation": "add",
                "params": {
                    "reservation_list": [{"mac": "02-00-00-00-00-01", "ip": "192.168.5.250"}]
                },
            },
        )
    ]


def test_modify_sends_original_and_replacement() -> None:
    sender = _RecordingSender()
    AddressReservationService(sender).modify(
        AddressReservation("02:00:00:00:00:01", "192.168.5.250"),
        AddressReservation("02:00:00:00:00:01", "192.168.5.251"),
    )
    assert sender.calls == [
        (
            "admin/client",
            "addr_reservation",
            {
                "operation": "modify",
                "params": {
                    "mac": "02-00-00-00-00-01",
                    "ip": "192.168.5.251",
                    "original_mac": "02-00-00-00-00-01",
                    "original_ip": "192.168.5.250",
                },
            },
        )
    ]


def test_remove_sends_mac_list() -> None:
    sender = _RecordingSender()
    AddressReservationService(sender).remove("02:00:00:00:00:01")
    assert sender.calls == [
        (
            "admin/client",
            "addr_reservation",
            {"operation": "remove", "params": {"reservation_list": ["02-00-00-00-00-01"]}},
        )
    ]


def test_add_rejects_invalid_ip() -> None:
    sender = _RecordingSender()
    with pytest.raises(ValueError, match="Failed to parse IPv4 address"):
        AddressReservationService(sender).add(AddressReservation("02:00:00:00:00:01", "300.1.1.1"))
    assert sender.calls == []
