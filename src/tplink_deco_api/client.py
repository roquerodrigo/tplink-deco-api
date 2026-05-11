from typing import Any

from . import endpoints
from .auth.protocol import build_payload, parse_response
from .auth.session import SessionContext
from .auth.transport import HttpTransport
from .crypto import generate_aes_pair, md5_session_hash, rsa_encrypt
from .exceptions import AuthenticationError
from .models import (
    ClientDevice,
    Device,
    DeviceMode,
    LoginResult,
    NetworkTotals,
    Performance,
    RsaKey,
    SessionKeys,
    WlanConfig,
)


class DecoClient:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        timeout: float = 10.0,
    ):
        self._host = host
        self._username = username
        self._password = password
        self._transport = HttpTransport(timeout=timeout)
        self._session: SessionContext | None = None

    def __enter__(self) -> "DecoClient":
        self.login()
        return self

    def __exit__(self, *_) -> None:
        self.logout()

    def login(self) -> LoginResult:
        auth_raw = self._transport.post_json(
            endpoints.login_url(self._host, "auth"),
            {"operation": "read"},
        )
        keys_raw = self._transport.post_json(
            endpoints.login_url(self._host, "keys"),
            {"operation": "read"},
        )

        sign_key = RsaKey.from_hex(*auth_raw["result"]["key"])
        pwd_key = RsaKey.from_hex(*keys_raw["result"]["password"])
        seq = auth_raw["result"]["seq"]

        aes_key, aes_iv = generate_aes_pair()
        session_hash = md5_session_hash(self._username, self._password)
        keys = SessionKeys(
            aes_key=aes_key, aes_iv=aes_iv, session_hash=session_hash, seq=seq
        )

        self._session = SessionContext(sign_key=sign_key, pwd_key=pwd_key, keys=keys)

        password_encrypted = rsa_encrypt(pwd_key.n, pwd_key.e, self._password.encode())
        login_body = build_payload(
            keys,
            sign_key,
            {"operation": "login", "params": {"password": password_encrypted}},
        )
        raw = self._transport.post_form(
            endpoints.login_url(self._host, "login"), login_body
        )

        result = parse_response(raw, keys)
        if "stok" not in result:
            raise AuthenticationError("Login falhou — stok ausente na resposta")

        self._session.stok = result["stok"]
        return LoginResult(stok=result["stok"], usr_lvl=result.get("usrLvl", 1))

    def logout(self) -> None:
        if self._session:
            self._session.invalidate()

    def is_authenticated(self) -> bool:
        return self._session is not None and self._session.is_authenticated()

    def request(self, path: str, form: str, data: dict[str, Any]) -> dict[str, Any]:
        self._require_auth()
        url = endpoints.admin_url(self._host, self._session.stok, path, form)
        body = build_payload(self._session.keys, self._session.sign_key, data)
        raw = self._transport.post_form(url, body)
        return parse_response(raw, self._session.keys)

    def get_device_list(self) -> list[Device]:
        result = self.request("admin/device", "device_list", {"operation": "read"})
        return [Device.from_api(d) for d in result.get("device_list", [])]

    def get_device_mode(self) -> DeviceMode:
        result = self.request("admin/device", "mode", {"operation": "read"})
        return DeviceMode.from_api(result)

    def get_wlan_config(self) -> WlanConfig:
        result = self.request("admin/wireless", "wlan", {"operation": "read"})
        return WlanConfig.from_api(result)

    def get_performance(self) -> Performance:
        result = self.request("admin/network", "performance", {"operation": "read"})
        return Performance.from_api(result)

    def get_client_list(self, deco_mac: str = "default") -> list[ClientDevice]:
        result = self.request(
            "admin/client",
            "client_list",
            {"operation": "read", "params": {"device_mac": deco_mac}},
        )
        return [ClientDevice.from_api(c) for c in result.get("client_list", [])]

    def get_client_totals(self, deco_mac: str = "default") -> NetworkTotals:
        return NetworkTotals.from_clients(self.get_client_list(deco_mac))

    def _require_auth(self) -> None:
        if not self.is_authenticated():
            raise AuthenticationError("Não autenticado — chame login() primeiro")
