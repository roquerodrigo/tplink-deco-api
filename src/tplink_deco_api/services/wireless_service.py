"""Wi-Fi networks and radio settings shared by the whole mesh."""

from __future__ import annotations

import string
from typing import TYPE_CHECKING

from .._json import get_bool, get_str
from ..models import WirelessBridge
from ..models._utils import encode_b64

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .._json import JsonObject, JsonValue
    from ..models import WlanBandName
    from ._request import RequestSender

_PATH = "admin/wireless"
_SSID_MAX_BYTES = 32
_PASSPHRASE_MIN_LENGTH = 8
_PASSPHRASE_MAX_LENGTH = 63
_HEX_KEY_LENGTH = 64
_HOST_ENABLE_KEYS: Mapping[str, str] = {
    "band2_4": "enable_2g",
    "band5_1": "enable_5g",
    "band5_2": "enable_5g2",
    "band6": "enable_6g",
    "band6_2": "enable_6g2",
}


class WirelessService:
    """Reads radio settings and edits the host and guest networks of each band."""

    def __init__(self, send: RequestSender) -> None:
        self._send = send

    def get_fast_roaming(self) -> bool:
        """Return whether 802.11r fast roaming is enabled."""
        return get_bool(self._read("ieee80211r"), "enable")

    def get_ht160_enabled(self) -> bool:
        """Return whether 160 MHz channels are allowed on 5 GHz."""
        return get_bool(self._read("bandwidth_enhance"), "enable_ht160")

    def get_operation_mode(self) -> str:
        """Return the Wi-Fi working mode, such as ``"AP"``."""
        return get_str(self._read("operation_mode"), "mode")

    def get_bridge(self) -> WirelessBridge:
        """Return the wireless backhaul status of the answering node."""
        return WirelessBridge.from_api(self._read("bridge"))

    def set_wlan(
        self,
        band: WlanBandName,
        *,
        guest: bool = False,
        ssid: str | None = None,
        password: str | None = None,
        enable: bool | None = None,
    ) -> None:
        """Change the SSID, password or on/off state of one band's host or guest network.

        Only the arguments that are not ``None`` are sent; the router keeps the
        rest. The firmware refuses to turn off the 2.4 GHz and 5 GHz host
        networks at the same time.
        """
        if band not in _HOST_ENABLE_KEYS:
            message = f"Failed to set wlan: unknown band {band!r}"
            raise ValueError(message)
        network: dict[str, JsonValue] = {}
        if ssid is not None:
            network["ssid"] = encode_b64(_require_ssid(ssid))
        if password is not None:
            network["password"] = encode_b64(_require_password(password))
        if enable is not None:
            network["enable" if guest else _HOST_ENABLE_KEYS[band]] = enable
        if not network:
            message = "Failed to set wlan: pass at least one of ssid, password or enable"
            raise ValueError(message)
        params: dict[str, JsonValue] = {band: {"guest" if guest else "host": network}}
        self._send(_PATH, "wlan", {"operation": "write", "params": params})

    def _read(self, form: str) -> JsonObject:
        return self._send(_PATH, form, {"operation": "read"})


def _require_ssid(value: str) -> str:
    if not value or len(value.encode()) > _SSID_MAX_BYTES:
        message = f"Failed to set wlan: SSID must be 1 to {_SSID_MAX_BYTES} bytes"
        raise ValueError(message)
    return value


def _require_password(value: str) -> str:
    is_passphrase = _PASSPHRASE_MIN_LENGTH <= len(value) <= _PASSPHRASE_MAX_LENGTH
    is_hex_key = len(value) == _HEX_KEY_LENGTH and all(c in string.hexdigits for c in value)
    if not (is_passphrase or is_hex_key):
        message = (
            f"Failed to set wlan: password must be {_PASSPHRASE_MIN_LENGTH} to"
            f" {_PASSPHRASE_MAX_LENGTH} characters or {_HEX_KEY_LENGTH} hex digits"
        )
        raise ValueError(message)
    return value
