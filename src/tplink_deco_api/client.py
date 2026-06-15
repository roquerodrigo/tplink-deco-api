"""High-level synchronous client for the TP-Link Deco HTTP API."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from . import endpoints
from ._json import JsonObject, JsonValue, get_int, get_object, get_str, get_str_tuple
from .auth.protocol import build_payload, parse_list_response, parse_response
from .auth.session import SessionContext
from .auth.transport import HttpTransport
from .crypto import generate_aes_pair, md5_session_hash, rsa_encrypt
from .exceptions import AuthenticationError
from .models import (
    ClientDevice,
    Device,
    DeviceMode,
    DslStatus,
    InternetStatus,
    LoginResult,
    LogType,
    NetworkTotals,
    Performance,
    TimeSettings,
    WanInfo,
    WirelessPower,
    WlanConfig,
)
from .models.rsa_key import RsaKey
from .models.session_keys import SessionKeys

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType

log: logging.Logger = logging.getLogger("tplink_deco_api.client")


class DecoClient:
    """High-level client that handles handshake, encryption and typed responses."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        timeout: float = 10.0,
    ) -> None:
        self._host = host
        self._username = username
        self._password = password
        self._transport = HttpTransport(timeout=timeout)
        self._session: SessionContext | None = None

    def __enter__(self) -> DecoClient:
        self.login()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.logout()

    def login(self) -> LoginResult:
        """Perform the RSA + AES handshake and obtain a session token."""
        auth_raw = self._transport.post_json(
            endpoints.login_url(self._host, "auth"),
            {"operation": "read"},
        )
        keys_raw = self._transport.post_json(
            endpoints.login_url(self._host, "keys"),
            {"operation": "read"},
        )

        sign_key_parts = get_str_tuple(_result(auth_raw), "key")
        pwd_key_parts = get_str_tuple(_result(keys_raw), "password")
        if len(sign_key_parts) < 2 or len(pwd_key_parts) < 2:
            raise AuthenticationError("Failed to login: RSA key handshake malformed")

        sign_key = RsaKey.from_hex(sign_key_parts[0], sign_key_parts[1])
        pwd_key = RsaKey.from_hex(pwd_key_parts[0], pwd_key_parts[1])
        seq = get_int(_result(auth_raw), "seq")

        aes_key, aes_iv = generate_aes_pair()
        session_hash = md5_session_hash(self._username, self._password)
        keys = SessionKeys(
            aes_key=aes_key,
            aes_iv=aes_iv,
            session_hash=session_hash,
            seq=seq,
        )
        self._session = SessionContext(sign_key=sign_key, pwd_key=pwd_key, keys=keys)

        password_encrypted = rsa_encrypt(pwd_key.n, pwd_key.e, self._password.encode())
        login_body = build_payload(
            keys,
            sign_key,
            {"operation": "login", "params": {"password": password_encrypted}},
        )
        raw = self._transport.post_form(endpoints.login_url(self._host, "login"), login_body)

        result = parse_response(raw, keys)
        stok = get_str(result, "stok")
        if not stok:
            raise AuthenticationError("Failed to login: missing stok in response")

        self._session.stok = stok
        log.info("Logged in to %s", self._host)
        return LoginResult(stok=stok, usr_lvl=get_int(result, "usrLvl", default=1))

    def logout(self) -> None:
        """Forget the session token, if any."""
        if self._session:
            self._session.invalidate()

    def is_authenticated(self) -> bool:
        """Return ``True`` while a valid session token is held."""
        return self._session is not None and self._session.is_authenticated()

    def request(
        self,
        path: str,
        form: str,
        data: Mapping[str, JsonValue],
    ) -> JsonObject:
        """Send an authenticated request and return the decrypted ``result``."""
        session = self._require_auth()
        url = endpoints.admin_url(self._host, session.stok, path, form)
        body = build_payload(session.keys, session.sign_key, data)
        raw = self._transport.post_form(url, body)
        return parse_response(raw, session.keys)

    def request_list(
        self,
        path: str,
        form: str,
        data: Mapping[str, JsonValue],
    ) -> list[JsonObject]:
        """Send an authenticated request and return the decrypted ``result`` as a list.

        Use instead of :meth:`request` when the endpoint returns a JSON array
        rather than a JSON object under the ``result`` key.
        """
        session = self._require_auth()
        url = endpoints.admin_url(self._host, session.stok, path, form)
        body = build_payload(session.keys, session.sign_key, data)
        raw = self._transport.post_form(url, body)
        return parse_list_response(raw, session.keys)

    def get_device_list(self) -> list[Device]:
        """Return all Deco mesh nodes."""
        result = self.request("admin/device", "device_list", {"operation": "read"})
        return [Device.from_api(item) for item in _list_of_objects(result, "device_list")]

    def get_device_mode(self) -> DeviceMode:
        """Return the device operating mode (router / AP / mesh)."""
        result = self.request("admin/device", "mode", {"operation": "read"})
        return DeviceMode.from_api(result)

    def get_wlan_config(self) -> WlanConfig:
        """Return the full Wi-Fi configuration across all bands."""
        result = self.request("admin/wireless", "wlan", {"operation": "read"})
        return WlanConfig.from_api(result)

    def get_performance(self) -> Performance:
        """Return CPU and memory usage of the gateway node."""
        result = self.request("admin/network", "performance", {"operation": "read"})
        return Performance.from_api(result)

    def get_client_list(self, deco_mac: str = "default") -> list[ClientDevice]:
        """Return every client connected to ``deco_mac`` (or all nodes by default)."""
        result = self.request(
            "admin/client",
            "client_list",
            {"operation": "read", "params": {"device_mac": deco_mac}},
        )
        return [ClientDevice.from_api(item) for item in _list_of_objects(result, "client_list")]

    def get_client_totals(self, deco_mac: str = "default") -> NetworkTotals:
        """Return aggregated up/down speeds across all clients."""
        return NetworkTotals.from_clients(self.get_client_list(deco_mac))

    def get_internet_status(self) -> InternetStatus:
        """Return WAN connection status including IPv4, IPv6 and physical link state."""
        result = self.request("admin/network", "internet", {"operation": "read"})
        return InternetStatus.from_api(result)

    def get_wan_info(self, device_mac: str = "default") -> WanInfo:
        """Return WAN and LAN IP configuration for ``device_mac``."""
        result = self.request(
            "admin/network",
            "wan_ipv4",
            {"operation": "read", "params": {"device_mac": device_mac}},
        )
        return WanInfo.from_api(result)

    def get_dsl_status(self, device_mac: str = "default") -> DslStatus:
        """Return DSL link status for ``device_mac``.

        Only meaningful on DSL-capable hardware. Some non-DSL models return an
        empty result, in which case every field defaults to an empty string or
        zero; others reject the ``dsl_status`` form and raise
        :class:`~tplink_deco_api.ApiError`. Callers targeting mixed hardware
        should be prepared to catch that exception.
        """
        result = self.request(
            "admin/network",
            "dsl_status",
            {"operation": "read", "params": {"device_mac": device_mac}},
        )
        return DslStatus.from_api(result)

    def get_wireless_power(self, device_mac: str = "default") -> WirelessPower:
        """Return transmit power settings for ``device_mac``."""
        result = self.request(
            "admin/wireless",
            "power",
            {"operation": "read", "params": {"device_mac": device_mac}},
        )
        return WirelessPower.from_api(result)

    def get_time_settings(self, device_mac: str = "default") -> TimeSettings:
        """Return date, time and timezone settings for ``device_mac``."""
        result = self.request(
            "admin/device",
            "timesetting",
            {"operation": "read", "params": {"device_mac": device_mac}},
        )
        return TimeSettings.from_api(result)

    def get_log_types(self) -> list[LogType]:
        """Return the list of log categories available for export."""
        items = self.request_list("admin/log_export", "types", {"operation": "read"})
        return [LogType.from_api(item) for item in items]

    def _require_auth(self) -> SessionContext:
        if self._session is None or not self._session.is_authenticated():
            raise AuthenticationError(
                "Failed to send request: not authenticated, call login() first"
            )
        return self._session


def _result(payload: JsonObject) -> JsonObject:
    return get_object(payload, "result")


def _list_of_objects(data: JsonObject, key: str) -> list[JsonObject]:
    value = data.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
