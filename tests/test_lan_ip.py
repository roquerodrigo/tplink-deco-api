"""Unit tests for the LAN IP reader and writer."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tplink_deco_api import DecoClient, LanIp

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tplink_deco_api._json import JsonObject, JsonValue

_LAN_IP = {
    "lan_ip": {"mask": "255.255.252.0", "ip": "192.0.2.1"},
    "dns_server_ip": ["198.51.100.53", "198.51.100.54"],
    "mac_addr": "00-11-22-33-44-55",
    "wan_ip": ["203.0.113.2"],
}


class _RecordingClient(DecoClient):
    def __init__(self, result: JsonObject | None = None) -> None:
        super().__init__("192.0.2.1", "admin", "secret")
        self.calls: list[tuple[str, str, Mapping[str, JsonValue]]] = []
        self._result: JsonObject = result or {}

    def request(self, path: str, form: str, data: Mapping[str, JsonValue]) -> JsonObject:
        self.calls.append((path, form, data))
        return self._result


def test_lan_ip_from_api() -> None:
    assert LanIp.from_api(_LAN_IP) == LanIp(
        ip="192.0.2.1",
        mask="255.255.252.0",
        mac="00:11:22:33:44:55",
        dns_servers=("198.51.100.53", "198.51.100.54"),
        wan_ips=("203.0.113.2",),
    )


def test_lan_ip_empty_payload_defaults() -> None:
    assert LanIp.from_api({}) == LanIp("", "", "", (), ())


def test_get_lan_ip_sends_device_mac() -> None:
    client = _RecordingClient(_LAN_IP)
    assert client.get_lan_ip().ip == "192.0.2.1"
    assert client.calls == [
        ("admin/network", "lan_ip", {"operation": "read", "params": {"device_mac": "default"}})
    ]


def test_set_lan_ip_sends_write() -> None:
    client = _RecordingClient()
    client.set_lan_ip("192.0.2.1", "255.255.255.0")
    assert client.calls == [
        (
            "admin/network",
            "lan_ip",
            {
                "operation": "write",
                "params": {
                    "device_mac": "default",
                    "lan_ip": {"ip": "192.0.2.1", "mask": "255.255.255.0"},
                },
            },
        )
    ]


@pytest.mark.parametrize(
    ("ip", "mask", "match"),
    [
        ("192.0.2.300", "255.255.255.0", "IPv4 address"),
        ("192.0.2.1", "255.0.255.0", "netmask"),
        ("192.0.2.1", "24", "netmask"),
        ("192.0.2.1", "0.0.0.255", "netmask"),
    ],
)
def test_set_lan_ip_rejects_bad_input_before_sending(ip: str, mask: str, match: str) -> None:
    client = _RecordingClient()
    with pytest.raises(ValueError, match=match):
        client.set_lan_ip(ip, mask)
    assert client.calls == []
