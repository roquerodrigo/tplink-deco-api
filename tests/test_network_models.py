"""Unit tests for the network status models (internet, WAN, DSL)."""

from __future__ import annotations

import pytest

from tplink_deco_api import (
    DecoError,
    DslStatus,
    InternetStatus,
    IpInfo,
    IpStatus,
    LanDetails,
    MobileStatus,
    WanDetails,
    WanInfo,
)


def test_internet_status_from_api() -> None:
    data = {
        "ipv4": {
            "inet_status": "online",
            "dial_status": "connected",
            "connect_type": "pppoe",
            "auto_detect_type": "pppoe",
            "error_code": 0,
        },
        "ipv6": {"inet_status": "offline", "error_code": 1},
        "link_status": "plugged",
    }
    status = InternetStatus.from_api(data)
    assert status.link_status == "plugged"
    assert status.ipv4 == IpStatus(
        inet_status="online",
        dial_status="connected",
        connect_type="pppoe",
        auto_detect_type="pppoe",
        error_code=0,
    )
    assert status.ipv6.inet_status == "offline"
    assert status.ipv6.error_code == 1


def test_internet_status_empty_payload_defaults() -> None:
    status = InternetStatus.from_api({})
    assert status.link_status == ""
    assert status.ipv4 == IpStatus("", "", "", "", 0)
    assert status.ipv6 == IpStatus("", "", "", "", 0)


def test_wan_info_from_api_normalizes_mac() -> None:
    data = {
        "wan": {
            "ip_info": {
                "ip": "152.250.100.220",
                "mask": "255.255.255.255",
                "mac": "0c-ef-15-e1-b2-17",
                "gateway": "200.204.21.21",
                "dns1": "1.1.1.1",
                "dns2": "9.9.9.9",
            },
            "dial_type": "pppoe",
            "enable_auto_dns": False,
        },
        "lan": {"ip_info": {"ip": "192.168.0.1", "mask": "255.255.255.0", "mac": ""}},
    }
    info = WanInfo.from_api(data)
    assert info.wan.dial_type == "pppoe"
    assert info.wan.enable_auto_dns is False
    assert info.wan.ip_info.mac == "0C:EF:15:E1:B2:17"
    assert info.wan.ip_info.dns2 == "9.9.9.9"
    assert info.lan.ip_info.ip == "192.168.0.1"
    assert info.lan.ip_info.gateway == ""


def test_wan_info_empty_payload_defaults() -> None:
    info = WanInfo.from_api({})
    assert info.wan == WanDetails(IpInfo("", "", "", "", "", ""), "", enable_auto_dns=False)
    assert info.lan == LanDetails(IpInfo("", "", "", "", "", ""))


def test_dsl_status_from_api() -> None:
    data = {
        "status": "up",
        "upstream_rate": 1000,
        "downstream_rate": 2000,
        "upstream_max_rate": 1200,
        "downstream_max_rate": 2400,
        "upstream_noise_margin": 6,
        "downstream_noise_margin": 7,
        "upstream_attenuation": 10,
        "downstream_attenuation": 12,
    }
    dsl = DslStatus.from_api(data)
    assert dsl.status == "up"
    assert dsl.downstream_rate == 2000
    assert dsl.downstream_attenuation == 12


def test_dsl_status_empty_payload_defaults_to_zero() -> None:
    """On non-DSL hardware that returns an empty result, all fields are zero."""
    dsl = DslStatus.from_api({})
    assert dsl.status == ""
    assert dsl.upstream_rate == 0
    assert dsl.downstream_rate == 0
    assert dsl.downstream_max_rate == 0
    assert dsl.downstream_attenuation == 0


_MOBILE_CPE = {
    "sim_number": "",
    "signal_strength": 60,
    "rsrp": -96,
    "snr": 24,
    "rssi": 0,
    "sim_status": "ready",
    "dial_status": "connected",
    "profile_name": "RXhhbXBsZQ==",
    "data_usage": 79648695,
    "rsrq": -11,
    "inet_status": "online",
    "downlink_rate": 1210,
    "limit_mode": "data_flow",
    "uplink_rate": 371,
    "network_type": "nr",
}


def test_mobile_status_from_api_decodes_profile_name() -> None:
    mobile = MobileStatus.from_api(_MOBILE_CPE)
    assert mobile == MobileStatus(
        inet_status="online",
        dial_status="connected",
        sim_status="ready",
        network_type="nr",
        signal_strength=60,
        rsrp=-96,
        rsrq=-11,
        snr=24,
        rssi=0,
        uplink_rate=371,
        downlink_rate=1210,
        data_usage=79648695,
        limit_mode="data_flow",
        profile_name="Example",
        sim_number="",
    )


def test_mobile_status_invalid_profile_name_raises() -> None:
    with pytest.raises(DecoError, match="Failed to decode base64 field"):
        MobileStatus.from_api({"profile_name": "/w=="})


def test_internet_status_mobile_gateway_derives_ipv4() -> None:
    """A 5G gateway sends only ``mobile_cpe``; ``ipv4`` is filled from it."""
    status = InternetStatus.from_api({"mobile_cpe": _MOBILE_CPE})
    assert status.mobile is not None
    assert status.mobile.network_type == "nr"
    assert status.ipv4 == IpStatus("online", "connected", "", "", 0)
    assert status.ipv6 == IpStatus("", "", "", "", 0)


def test_internet_status_prefers_explicit_ipv4_over_mobile() -> None:
    data = {
        "ipv4": {"inet_status": "offline", "dial_status": "disconnected"},
        "mobile_cpe": _MOBILE_CPE,
    }
    status = InternetStatus.from_api(data)
    assert status.ipv4.inet_status == "offline"
    assert status.mobile is not None


def test_internet_status_wired_gateway_has_no_mobile() -> None:
    assert InternetStatus.from_api({"ipv4": {"inet_status": "online"}}).mobile is None


def test_wan_info_lte_reads_mobile_cpe_addressing() -> None:
    data = {
        "wan": {
            "mobile_cpe": {
                "mac": "00-11-22-33-44-55",
                "dns2": "198.51.100.54",
                "dns1": "198.51.100.53",
                "mask": "255.255.255.252",
                "gateway": "203.0.113.1",
                "ip": "203.0.113.2",
            },
            "dial_type": "lte",
        },
        "lan": {
            "ip_info": {"mac": "00-11-22-33-44-66", "mask": "255.255.252.0", "ip": "192.0.2.1"}
        },
    }
    info = WanInfo.from_api(data)
    assert info.wan.dial_type == "lte"
    assert info.wan.ip_info == IpInfo(
        ip="203.0.113.2",
        mask="255.255.255.252",
        mac="00:11:22:33:44:55",
        gateway="203.0.113.1",
        dns1="198.51.100.53",
        dns2="198.51.100.54",
    )
    assert info.lan.ip_info.ip == "192.0.2.1"
