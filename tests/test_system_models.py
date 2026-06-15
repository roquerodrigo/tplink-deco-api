"""Unit tests for wireless/time/log models and the list response parser."""

from __future__ import annotations

import json

import pytest

from tplink_deco_api import ApiError, LogType, TimeSettings, WirelessPower
from tplink_deco_api.auth.protocol import parse_list_response
from tplink_deco_api.crypto import aes_encrypt
from tplink_deco_api.models.session_keys import SessionKeys

_KEYS = SessionKeys(
    aes_key="1234567890123456",
    aes_iv="6543210987654321",
    session_hash="a" * 32,
    seq=1,
)


def test_wireless_power_from_api() -> None:
    assert WirelessPower.from_api({"support_dfs": True}).support_dfs is True
    assert WirelessPower.from_api({}).support_dfs is False


def test_time_settings_from_api() -> None:
    data = {
        "time": "21:10:30",
        "date": "06/14/2026",
        "timezone": "-180",
        "tz_region": "Sao_Paulo",
        "continent": "America",
        "dst_status": "",
    }
    ts = TimeSettings.from_api(data)
    assert ts == TimeSettings("21:10:30", "06/14/2026", "-180", "Sao_Paulo", "America", "")


def test_time_settings_empty_payload_defaults() -> None:
    assert TimeSettings.from_api({}) == TimeSettings("", "", "", "", "", "")


def test_log_type_from_api() -> None:
    assert LogType.from_api({"name": "ALL", "value": 8}) == LogType("ALL", 8)


def _encrypt(inner: object) -> str:
    return aes_encrypt(_KEYS.aes_key, _KEYS.aes_iv, json.dumps(inner))


def test_parse_list_response_ok() -> None:
    inner = {"result": [{"name": "ALL", "value": 8}, {"name": "INFO", "value": 6}], "error_code": 0}
    items = parse_list_response({"data": _encrypt(inner)}, _KEYS)
    assert items == [{"name": "ALL", "value": 8}, {"name": "INFO", "value": 6}]


def test_parse_list_response_drops_non_objects() -> None:
    inner = {"result": [{"name": "ALL"}, 1, "x", None], "error_code": 0}
    assert parse_list_response({"data": _encrypt(inner)}, _KEYS) == [{"name": "ALL"}]


def test_parse_list_response_non_list_result_is_empty() -> None:
    inner = {"result": {"not": "a list"}, "error_code": 0}
    assert parse_list_response({"data": _encrypt(inner)}, _KEYS) == []


def test_parse_list_response_missing_data() -> None:
    with pytest.raises(ApiError):
        parse_list_response({}, _KEYS)


def test_parse_list_response_empty_data() -> None:
    with pytest.raises(ApiError):
        parse_list_response({"data": ""}, _KEYS)


def test_parse_list_response_error_code() -> None:
    with pytest.raises(ApiError) as exc:
        parse_list_response({"data": _encrypt({"result": [], "error_code": -5002})}, _KEYS)
    assert exc.value.error_code == -5002


def test_parse_list_response_non_object_payload() -> None:
    with pytest.raises(ApiError):
        parse_list_response({"data": _encrypt([1, 2, 3])}, _KEYS)
