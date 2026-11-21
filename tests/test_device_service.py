"""Unit tests for ``DeviceService.reboot``; the request is recorded, never sent."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tplink_deco_api import DeviceService

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


def _service(result: JsonObject | None = None) -> tuple[DeviceService, _RecordingSender]:
    sender = _RecordingSender(result)
    return DeviceService(sender), sender


def test_reboot_sends_mac_list_in_router_format() -> None:
    service, sender = _service()
    service.reboot("00:11:22:33:44:55", "00-11-22-33-44-aa")
    assert sender.calls == [
        (
            "admin/device",
            "system",
            {
                "operation": "reboot",
                "params": {
                    "mac_list": [{"mac": "00-11-22-33-44-55"}, {"mac": "00-11-22-33-44-AA"}]
                },
            },
        )
    ]


def test_reboot_requires_a_mac() -> None:
    service, sender = _service()
    with pytest.raises(ValueError, match="at least one node MAC"):
        service.reboot()
    assert sender.calls == []


def test_reboot_rejects_malformed_mac_before_sending() -> None:
    service, sender = _service()
    with pytest.raises(ValueError, match="MAC address"):
        service.reboot("not-a-mac")
    assert sender.calls == []
