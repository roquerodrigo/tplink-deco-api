"""Network-free unit tests for ``DecoClient`` login and request flow.

The HTTP layer is replaced by a fake transport that returns real
AES-encrypted envelopes, so the full crypto/protocol/session path runs
in-process without ever touching a router.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tplink_deco_api import (
    ApiError,
    AuthenticationError,
    ClientDevice,
    DecoClient,
    Device,
    DeviceMode,
    NetworkTotals,
    Performance,
    WlanConfig,
)
from tplink_deco_api.auth.protocol import build_payload, parse_response
from tplink_deco_api.crypto import aes_encrypt
from tplink_deco_api.models.session_keys import SessionKeys

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tplink_deco_api._json import JsonObject

_SIGN_N = int(
    "DE1E5BD8347A6BED75ED9E96190B47FDCE5696B49A542F908003D01DD3CBF59B"
    "9A76F42A68048D85B1E3AFC78CD23191AA26CD69E5932D4CA02F35687071F65F",
    16,
)
_SIGN_N_HEX = format(_SIGN_N, "x")
_E_HEX = "010001"


class _FakeTransport:
    """Stand-in for ``HttpTransport`` that serves canned handshake + encrypted bodies.

    ``login()`` issues three POSTs (auth, keys, login). The first two are plain
    JSON; the login one returns an AES envelope encrypted with the AES key/IV the
    client generated, which the fake reads back out of the posted form body.
    """

    def __init__(self, *, result_for_form: Mapping[str, JsonObject] | None = None) -> None:
        self.result_for_form = dict(result_for_form or {})
        self.posted_urls: list[str] = []
        self._aes_key = ""
        self._aes_iv = ""
        self.login_stok = "deadbeefstoktoken"
        self.login_usr_lvl = 2

    def post_json(self, url: str, body: Mapping[str, str]) -> JsonObject:
        self.posted_urls.append(url)
        if "form=auth" in url:
            return {"result": {"key": [_SIGN_N_HEX, _E_HEX], "seq": 100}}
        if "form=keys" in url:
            return {"result": {"password": [_SIGN_N_HEX, _E_HEX]}}
        raise AssertionError(f"unexpected post_json url: {url}")

    def post_form(self, url: str, body: str) -> JsonObject:
        self.posted_urls.append(url)
        self._capture_aes(body)
        if "form=login" in url:
            inner = {
                "result": {"stok": self.login_stok, "usrLvl": self.login_usr_lvl},
                "error_code": 0,
            }
            return self._envelope(inner)
        form = url.rsplit("form=", 1)[-1]
        result = self.result_for_form.get(form, {})
        return self._envelope({"result": result, "error_code": 0})

    def _capture_aes(self, body: str) -> None:
        # The fake decrypts the sign block off-band by re-deriving the AES pair
        # from the most recent client. Instead we recover key/iv from the keys
        # the client stored: the test passes them in via ``set_aes``.
        pass

    def set_aes(self, aes_key: str, aes_iv: str) -> None:
        self._aes_key = aes_key
        self._aes_iv = aes_iv

    def _envelope(self, inner: JsonObject) -> JsonObject:
        data_b64 = aes_encrypt(self._aes_key, self._aes_iv, json.dumps(inner))
        return {"data": data_b64}


def _make_client(
    transport: _FakeTransport,
) -> DecoClient:
    client = DecoClient("192.0.2.1", "admin", "secret")
    client._transport = transport  # type: ignore[assignment]
    return client


def _login(client: DecoClient, transport: _FakeTransport) -> None:
    """Drive login, wiring the fake's AES pair to whatever the client generated."""
    real_post_form = transport.post_form

    def wrapped(url: str, body: str) -> JsonObject:
        keys = client._session.keys if client._session else None
        if keys is not None:
            transport.set_aes(keys.aes_key, keys.aes_iv)
        return real_post_form(url, body)

    transport.post_form = wrapped  # type: ignore[assignment]


def test_login_success_sets_session() -> None:
    transport = _FakeTransport()
    client = _make_client(transport)
    _login(client, transport)

    result = client.login()

    assert result.stok == transport.login_stok
    assert result.usr_lvl == 2
    assert client.is_authenticated()
    assert any("form=auth" in u for u in transport.posted_urls)
    assert any("form=keys" in u for u in transport.posted_urls)
    assert any("form=login" in u for u in transport.posted_urls)


def test_login_seq_propagates_to_session() -> None:
    transport = _FakeTransport()
    client = _make_client(transport)
    _login(client, transport)
    client.login()
    assert client._session is not None
    assert client._session.keys.seq == 100


def test_login_malformed_rsa_keys_raises() -> None:
    transport = _FakeTransport()

    def bad_post_json(url: str, body: Mapping[str, str]) -> JsonObject:
        if "form=auth" in url:
            return {"result": {"key": [_SIGN_N_HEX], "seq": 1}}  # only one element
        return {"result": {"password": [_SIGN_N_HEX, _E_HEX]}}

    transport.post_json = bad_post_json  # type: ignore[assignment]
    client = _make_client(transport)
    with pytest.raises(AuthenticationError, match="RSA key handshake malformed"):
        client.login()


def test_login_missing_stok_raises() -> None:
    transport = _FakeTransport()
    transport.login_stok = ""
    client = _make_client(transport)
    _login(client, transport)
    with pytest.raises(AuthenticationError, match="missing stok"):
        client.login()


def test_login_default_usr_lvl() -> None:
    transport = _FakeTransport()
    client = _make_client(transport)
    _login(client, transport)
    # Drop usr_lvl from the login envelope to exercise the default.
    real_post_form = transport.post_form

    def patched(url: str, body: str) -> JsonObject:
        if "form=login" in url:
            keys = client._session.keys if client._session else None
            assert keys is not None
            transport.set_aes(keys.aes_key, keys.aes_iv)
            inner = {"result": {"stok": "tok"}, "error_code": 0}
            return transport._envelope(inner)
        return real_post_form(url, body)

    transport.post_form = patched  # type: ignore[assignment]
    result = client.login()
    assert result.usr_lvl == 1


def test_request_before_login_raises() -> None:
    client = DecoClient("192.0.2.1", "admin", "secret")
    with pytest.raises(AuthenticationError, match="not authenticated"):
        client.request("admin/device", "device_list", {"operation": "read"})


def test_logout_invalidates_session() -> None:
    transport = _FakeTransport()
    client = _make_client(transport)
    _login(client, transport)
    client.login()
    assert client.is_authenticated()
    client.logout()
    assert not client.is_authenticated()
    assert client._session is not None
    assert client._session.keys.seq == 0


def test_logout_without_session_is_noop() -> None:
    client = DecoClient("192.0.2.1", "admin", "secret")
    client.logout()
    assert not client.is_authenticated()


def test_is_authenticated_false_initially() -> None:
    client = DecoClient("192.0.2.1", "admin", "secret")
    assert not client.is_authenticated()


def _logged_in(result_for_form: Mapping[str, JsonObject]) -> tuple[DecoClient, _FakeTransport]:
    transport = _FakeTransport(result_for_form=result_for_form)
    client = _make_client(transport)
    _login(client, transport)
    client.login()
    # After login the AES pair is fixed; subsequent forms reuse it.
    assert client._session is not None
    transport.set_aes(client._session.keys.aes_key, client._session.keys.aes_iv)
    return client, transport


def test_get_device_list() -> None:
    payload = {
        "device_list": [
            {"mac": "0c-ef-15-e1-b2-16", "device_model": "BE65"},
            {"mac": "aa:bb:cc:dd:ee:ff", "device_model": "X20"},
            "not-an-object",
        ]
    }
    client, _ = _logged_in({"device_list": payload})
    devices = client.get_device_list()
    assert all(isinstance(d, Device) for d in devices)
    assert len(devices) == 2
    assert devices[0].mac == "0C:EF:15:E1:B2:16"
    assert devices[0].device_model == "BE65"


def test_get_device_list_missing_key_returns_empty() -> None:
    client, _ = _logged_in({"device_list": {}})
    assert client.get_device_list() == []


def test_get_device_mode() -> None:
    payload = {"workmode": "router", "sysmode": "router", "region": {"device": "EU"}}
    client, _ = _logged_in({"mode": payload})
    mode = client.get_device_mode()
    assert isinstance(mode, DeviceMode)
    assert mode.workmode == "router"
    assert mode.region == "EU"


def test_get_wlan_config() -> None:
    payload = {"band2_4": {"host": {"ssid": "", "channel": 6}}}
    client, _ = _logged_in({"wlan": payload})
    wlan = client.get_wlan_config()
    assert isinstance(wlan, WlanConfig)
    assert wlan.band2_4.host.channel == 6


def test_get_performance() -> None:
    client, _ = _logged_in({"performance": {"cpu_usage": 0.05, "mem_usage": 0.42}})
    perf = client.get_performance()
    assert isinstance(perf, Performance)
    assert perf.cpu_usage == pytest.approx(0.05)
    assert perf.mem_usage == pytest.approx(0.42)


def test_get_client_list() -> None:
    payload = {
        "client_list": [
            {"mac": "AA:BB:CC:DD:EE:01", "up_speed": 100, "down_speed": 200},
            {"mac": "AA:BB:CC:DD:EE:02", "up_speed": 50, "down_speed": 75},
        ]
    }
    client, _ = _logged_in({"client_list": payload})
    clients = client.get_client_list()
    assert all(isinstance(c, ClientDevice) for c in clients)
    assert len(clients) == 2
    assert clients[0].up_speed == 100


def test_get_client_list_custom_mac_in_request() -> None:
    payload = {"client_list": []}
    client, transport = _logged_in({"client_list": payload})
    client.get_client_list(deco_mac="AA:BB:CC:DD:EE:FF")
    assert any("form=client_list" in u for u in transport.posted_urls)


def test_get_client_totals() -> None:
    payload = {
        "client_list": [
            {"mac": "AA:BB:CC:DD:EE:01", "up_speed": 100, "down_speed": 200},
            {"mac": "AA:BB:CC:DD:EE:02", "up_speed": 50, "down_speed": 75},
        ]
    }
    client, _ = _logged_in({"client_list": payload})
    totals = client.get_client_totals()
    assert isinstance(totals, NetworkTotals)
    assert totals.up_speed == 150
    assert totals.down_speed == 275


def test_request_url_includes_stok() -> None:
    client, transport = _logged_in({"mode": {"workmode": "router", "sysmode": "router"}})
    client.get_device_mode()
    admin_urls = [u for u in transport.posted_urls if "admin/device" in u]
    assert admin_urls
    assert f";stok={transport.login_stok}/" in admin_urls[-1]


def test_request_propagates_api_error() -> None:
    transport = _FakeTransport()
    client = _make_client(transport)
    _login(client, transport)
    client.login()
    assert client._session is not None
    keys = client._session.keys
    transport.set_aes(keys.aes_key, keys.aes_iv)

    real_post_form = transport.post_form

    def error_post(url: str, body: str) -> JsonObject:
        if "form=mode" in url:
            inner = {"result": {}, "error_code": -5002}
            return transport._envelope(inner)
        return real_post_form(url, body)

    transport.post_form = error_post  # type: ignore[assignment]
    with pytest.raises(ApiError) as exc:
        client.get_device_mode()
    assert exc.value.error_code == -5002


def test_context_manager_logs_in_and_out() -> None:
    transport = _FakeTransport()
    client = _make_client(transport)
    _login(client, transport)
    with client as ctx:
        assert ctx is client
        assert client.is_authenticated()
    assert not client.is_authenticated()


def test_build_and_parse_roundtrip_matches_client_payload() -> None:
    """Sanity check that the protocol encode/decode the client relies on roundtrips."""
    keys = SessionKeys(
        aes_key="1234567890123456",
        aes_iv="6543210987654321",
        session_hash="a" * 32,
        seq=5,
    )
    from tplink_deco_api.models.rsa_key import RsaKey

    sign_key = RsaKey(n=_SIGN_N, e=0x10001)
    body = build_payload(keys, sign_key, {"operation": "read"})
    assert body.startswith("sign=")
    inner = {"result": {"ok": True}, "error_code": 0}
    envelope = {"data": aes_encrypt(keys.aes_key, keys.aes_iv, json.dumps(inner))}
    assert parse_response(envelope, keys) == {"ok": True}
