"""Unit tests for the wireless setting readers and the ``set_wlan`` writer."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tplink_deco_api import DecoClient, WirelessBridge

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tplink_deco_api import WlanBandName
    from tplink_deco_api._json import JsonObject, JsonValue

_PHRASE = "correct horse"


class _RecordingClient(DecoClient):
    def __init__(self, result: JsonObject | None = None) -> None:
        super().__init__("192.0.2.1", "admin", "secret")
        self.calls: list[tuple[str, str, Mapping[str, JsonValue]]] = []
        self._result: JsonObject = result or {}

    def request(self, path: str, form: str, data: Mapping[str, JsonValue]) -> JsonObject:
        self.calls.append((path, form, data))
        return self._result


def test_get_fast_roaming() -> None:
    client = _RecordingClient({"enable": True})
    assert client.get_fast_roaming() is True
    assert client.calls == [("admin/wireless", "ieee80211r", {"operation": "read"})]


def test_get_ht160_enabled() -> None:
    client = _RecordingClient({"enable_ht160": True})
    assert client.get_ht160_enabled() is True
    assert client.calls[0][1] == "bandwidth_enhance"


def test_get_wireless_operation_mode() -> None:
    client = _RecordingClient({"mode": "AP"})
    assert client.get_wireless_operation_mode() == "AP"
    assert client.calls[0][1] == "operation_mode"


def test_get_wireless_bridge() -> None:
    client = _RecordingClient({"support_plc": False, "location": "good", "status": "getting"})
    assert client.get_wireless_bridge() == WirelessBridge(
        status="getting", location="good", support_plc=False
    )
    assert client.calls[0][1] == "bridge"


def test_wireless_bridge_empty_payload_defaults() -> None:
    assert WirelessBridge.from_api({}) == WirelessBridge("", "", support_plc=False)


def test_set_wlan_host_sends_base64_and_band_enable_key() -> None:
    client = _RecordingClient()
    client.set_wlan("band5_1", ssid="Example", password=_PHRASE, enable=True)
    assert client.calls == [
        (
            "admin/wireless",
            "wlan",
            {
                "operation": "write",
                "params": {
                    "band5_1": {
                        "host": {
                            "ssid": "RXhhbXBsZQ==",
                            "password": "Y29ycmVjdCBob3JzZQ==",
                            "enable_5g": True,
                        }
                    }
                },
            },
        )
    ]


@pytest.mark.parametrize(
    ("band", "key"),
    [
        ("band2_4", "enable_2g"),
        ("band5_2", "enable_5g2"),
        ("band6", "enable_6g"),
        ("band6_2", "enable_6g2"),
    ],
)
def test_set_wlan_host_enable_key_per_band(band: WlanBandName, key: str) -> None:
    client = _RecordingClient()
    client.set_wlan(band, enable=False)
    assert client.calls[0][2]["params"] == {band: {"host": {key: False}}}


def test_set_wlan_guest_uses_plain_enable() -> None:
    client = _RecordingClient()
    client.set_wlan("band2_4", guest=True, enable=True, ssid="Guest")
    assert client.calls[0][2]["params"] == {
        "band2_4": {"guest": {"ssid": "R3Vlc3Q=", "enable": True}}
    }


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({}, "at least one"),
        ({"ssid": ""}, "SSID"),
        ({"ssid": "x" * 33}, "SSID"),
        ({"ssid": "é" * 17}, "SSID"),
        ({"password": "short"}, "password"),
        ({"password": "x" * 64}, "password"),
    ],
)
def test_set_wlan_rejects_bad_input_before_sending(kwargs: dict[str, str], match: str) -> None:
    client = _RecordingClient()
    with pytest.raises(ValueError, match=match):
        client.set_wlan("band2_4", **kwargs)  # type: ignore[arg-type]
    assert client.calls == []


def test_set_wlan_rejects_unknown_band() -> None:
    client = _RecordingClient()
    with pytest.raises(ValueError, match="unknown band"):
        client.set_wlan("band7", enable=True)  # type: ignore[arg-type]
    assert client.calls == []
