"""Unit tests for the network status models (internet, WAN, DSL)."""

from __future__ import annotations

from tplink_deco_api import (
    DslStatus,
    InternetStatus,
    IpInfo,
    IpStatus,
    LanDetails,
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
    assert info.wan == WanDetails(IpInfo("", "", "", "", "", ""), "", False)
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
