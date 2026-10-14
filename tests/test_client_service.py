"""Unit tests for ``ClientService`` request payloads and blocklist parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tplink_deco_api import BlockedClient, ClientService

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


def test_update_sends_user_set_name() -> None:
    sender = _RecordingSender()
    ClientService(sender).update("6a:7a:d6:9b:16:7f", "Apple Watch")
    assert sender.calls == [
        (
            "admin/client",
            "client_list",
            {
                "operation": "write",
                "params": {
                    "client_list": [
                        {
                            "mac": "6A-7A-D6-9B-16-7F",
                            "name": "QXBwbGUgV2F0Y2g=",
                            "user_set_name_type": True,
                        }
                    ]
                },
            },
        )
    ]


def test_update_includes_client_type_when_given() -> None:
    sender = _RecordingSender()
    ClientService(sender).update("6A-7A-D6-9B-16-7F", "Watch", client_type="pc")
    entry = sender.calls[0][2]["params"]["client_list"][0]  # type: ignore[index]
    assert entry["client_type"] == "pc"  # type: ignore[index]


def test_update_rejects_blank_name() -> None:
    sender = _RecordingSender()
    with pytest.raises(ValueError, match="name must not be blank"):
        ClientService(sender).update("6A-7A-D6-9B-16-7F", "  ")
    assert sender.calls == []


def test_update_rejects_malformed_mac() -> None:
    sender = _RecordingSender()
    with pytest.raises(ValueError, match="Failed to parse MAC address"):
        ClientService(sender).update("not-a-mac", "Watch")
    assert sender.calls == []


def test_remove_sends_mac_entry() -> None:
    sender = _RecordingSender()
    ClientService(sender).remove("14:35:b7:74:06:5c")
    assert sender.calls == [
        (
            "admin/client",
            "client_list",
            {"operation": "remove", "params": {"client_list": [{"mac": "14-35-B7-74-06-5C"}]}},
        )
    ]


def test_block_sends_labelled_entry() -> None:
    sender = _RecordingSender()
    ClientService(sender).block("02:00:00:00:00:01", "Test", "other")
    assert sender.calls == [
        (
            "admin/client",
            "black_list",
            {
                "operation": "block",
                "params": {
                    "client_list": [
                        {"mac": "02-00-00-00-00-01", "name": "VGVzdA==", "client_type": "other"}
                    ]
                },
            },
        )
    ]


def test_unblock_sends_bare_mac() -> None:
    sender = _RecordingSender()
    ClientService(sender).unblock("02:00:00:00:00:01")
    assert sender.calls == [
        (
            "admin/client",
            "black_list",
            {"operation": "unblock", "params": {"client_list": ["02-00-00-00-00-01"]}},
        )
    ]


def test_get_blocked_parses_entries() -> None:
    sender = _RecordingSender(
        {"client_list": [{"mac": "02-00-00-00-00-01", "name": "VGVzdA==", "client_type": "other"}]}
    )
    assert ClientService(sender).get_blocked() == [
        BlockedClient(mac="02:00:00:00:00:01", name="Test", client_type="other")
    ]
    assert sender.calls == [("admin/client", "black_list", {"operation": "list"})]


def test_get_blocked_empty_object_returns_empty_list() -> None:
    sender = _RecordingSender({"client_list": {}})
    assert ClientService(sender).get_blocked() == []
