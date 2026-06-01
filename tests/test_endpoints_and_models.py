"""Unit tests for URL builders, the protocol decode boundary, utils and models."""

from __future__ import annotations

import json

import pytest

from tplink_deco_api import (
    ApiError,
    ClientDevice,
    Device,
    DeviceMode,
    IotHost,
    MloHost,
    Performance,
    SignalLevel,
    TransportError,
    WlanConfig,
    endpoints,
)
from tplink_deco_api.auth.protocol import parse_response
from tplink_deco_api.crypto import aes_encrypt
from tplink_deco_api.models._utils import decode_b64, normalize_mac
from tplink_deco_api.models.rsa_key import RsaKey
from tplink_deco_api.models.session_keys import SessionKeys

_KEYS = SessionKeys(
    aes_key="1234567890123456",
    aes_iv="6543210987654321",
    session_hash="a" * 32,
    seq=1,
)


def test_is_plain_known_and_unknown() -> None:
    assert endpoints.is_plain("/login?form=auth")
    assert not endpoints.is_plain("/admin/device?form=device_list")


def test_login_url() -> None:
    assert endpoints.login_url("192.0.2.1", "auth") == (
        "http://192.0.2.1/cgi-bin/luci/;stok=/login?form=auth"
    )


def test_admin_url() -> None:
    assert endpoints.admin_url("192.0.2.1", "TOK", "admin/device", "device_list") == (
        "http://192.0.2.1/cgi-bin/luci/;stok=TOK/admin/device?form=device_list"
    )


def test_parse_response_non_object_payload_wrapped() -> None:
    """A decrypted JSON value that is not an object maps to an ApiError(-1)."""
    data_b64 = aes_encrypt(_KEYS.aes_key, _KEYS.aes_iv, json.dumps([1, 2, 3]))
    with pytest.raises(ApiError) as exc:
        parse_response({"data": data_b64}, _KEYS)
    assert exc.value.error_code == -1


def test_parse_response_errorcode_alias() -> None:
    inner = {"result": {}, "errorcode": -42}
    data_b64 = aes_encrypt(_KEYS.aes_key, _KEYS.aes_iv, json.dumps(inner))
    with pytest.raises(ApiError) as exc:
        parse_response({"data": data_b64}, _KEYS)
    assert exc.value.error_code == -42


def test_decode_b64_roundtrip_and_empty() -> None:
    from base64 import b64encode

    assert decode_b64("") == ""
    encoded = b64encode(b"My Network").decode()
    assert decode_b64(encoded) == "My Network"


def test_normalize_mac() -> None:
    assert normalize_mac("aa-bb-cc-dd-ee-ff") == "AA:BB:CC:DD:EE:FF"
    assert normalize_mac("aa:bb:cc:dd:ee:ff") == "AA:BB:CC:DD:EE:FF"
    assert normalize_mac("") == ""


def test_rsa_key_from_hex() -> None:
    key = RsaKey.from_hex("ff", "10001")
    assert key.n == 255
    assert key.e == 0x10001


def test_device_from_api_decodes_fields() -> None:
    device = Device.from_api(
        {
            "mac": "0c-ef-15-e1-b2-16",
            "device_model": "BE65",
            "bssid_2g": "12-ef-15-e1-b2-18",
            "set_gateway_support": True,
            "signal_level": {"band2_4": "1", "band5": "2", "band6": "3"},
        }
    )
    assert device.mac == "0C:EF:15:E1:B2:16"
    assert device.bssid_2g == "12:EF:15:E1:B2:18"
    assert device.set_gateway_support is True
    assert device.signal_level.band6 == "3"


def test_signal_level_defaults() -> None:
    level = SignalLevel.from_api({})
    assert level.band2_4 == "0"
    assert level.band5 == "0"
    assert level.band6 == "0"


def test_device_mode_region_default() -> None:
    mode = DeviceMode.from_api({"workmode": "router", "sysmode": "router"})
    assert mode.region == ""


def test_performance_from_api() -> None:
    perf = Performance.from_api({"cpu_usage": 0.05, "mem_usage": 0.42})
    assert perf.cpu_usage == pytest.approx(0.05)


def test_client_device_from_api() -> None:
    client = ClientDevice.from_api(
        {"mac": "aa:bb:cc:dd:ee:ff", "up_speed": 10, "down_speed": 20, "online": True}
    )
    assert client.mac == "AA:BB:CC:DD:EE:FF"
    assert client.up_speed == 10
    assert client.online is True


def test_wlan_config_from_api_full() -> None:
    wlan = WlanConfig.from_api(
        {
            "band2_4": {
                "host": {"ssid": "", "channel": 6},
                "guest": {"ssid": "", "vlan_id": 5, "need_set_vlan": True},
                "backhaul": {"channel": 1},
            },
            "iot": {"host": {"ssid": "", "enable": True}},
            "mlo": {"host": {"ssid": "", "band": ["2.4G", "5G"]}},
            "is_eg": True,
        }
    )
    assert wlan.band2_4.host.channel == 6
    assert wlan.band2_4.guest.vlan_id == 5
    assert wlan.band2_4.guest.need_set_vlan is True
    assert wlan.band2_4.backhaul.channel == 1
    assert isinstance(wlan.iot_host, IotHost)
    assert isinstance(wlan.mlo_host, MloHost)
    assert wlan.mlo_host.band == ("2.4G", "5G")
    assert wlan.is_eg is True


def test_wlan_guest_optional_fields_absent() -> None:
    wlan = WlanConfig.from_api({"band2_4": {"guest": {"ssid": "", "enable": True}}})
    assert wlan.band2_4.guest.vlan_id is None
    assert wlan.band2_4.guest.need_set_vlan is None


def test_transport_error_default_status_code() -> None:
    err = TransportError("boom")
    assert err.status_code is None
    assert str(err) == "boom"
