"""Unit tests for ``DecoClient.reboot``; the request is recorded, never sent."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tplink_deco_api import DecoClient

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tplink_deco_api._json import JsonObject, JsonValue


class _RecordingClient(DecoClient):
    def __init__(self) -> None:
        super().__init__("192.0.2.1", "admin", "secret")
        self.calls: list[tuple[str, str, Mapping[str, JsonValue]]] = []

    def request(self, path: str, form: str, data: Mapping[str, JsonValue]) -> JsonObject:
        self.calls.append((path, form, data))
        return {}


def test_reboot_sends_mac_list_in_router_format() -> None:
    client = _RecordingClient()
    client.reboot("00:11:22:33:44:55", "00-11-22-33-44-aa")
    assert client.calls == [
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
    client = _RecordingClient()
    with pytest.raises(ValueError, match="at least one node MAC"):
        client.reboot()
    assert client.calls == []


def test_reboot_rejects_malformed_mac_before_sending() -> None:
    client = _RecordingClient()
    with pytest.raises(ValueError, match="MAC address"):
        client.reboot("not-a-mac")
    assert client.calls == []
