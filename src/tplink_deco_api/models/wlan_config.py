"""Wi-Fi configuration: bands, guest networks, IoT and MLO hosts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .._json import JsonObject, get_bool, get_int, get_object, get_str, get_str_tuple
from ._utils import decode_b64

type WlanBandName = Literal["band2_4", "band5_1", "band5_2", "band6", "band6_2"]


@dataclass(frozen=True)
class WlanHost:
    """Primary SSID configuration for a single radio band."""

    ssid: str
    password: str
    channel: int
    enable: bool
    mode: str
    channel_width: str
    enable_hide_ssid: bool

    @classmethod
    def from_api(cls, data: JsonObject) -> WlanHost:
        """Build ``WlanHost`` from a router payload."""
        return cls(
            ssid=decode_b64(get_str(data, "ssid")),
            password=decode_b64(get_str(data, "password")),
            channel=get_int(data, "channel"),
            enable=get_bool(data, "enable"),
            mode=get_str(data, "mode"),
            channel_width=get_str(data, "channel_width"),
            enable_hide_ssid=get_bool(data, "enable_hide_ssid"),
        )


@dataclass(frozen=True)
class WlanGuest:
    """Guest SSID configuration."""

    ssid: str
    password: str
    enable: bool
    vlan_id: int | None = None
    need_set_vlan: bool | None = None

    @classmethod
    def from_api(cls, data: JsonObject) -> WlanGuest:
        """Build ``WlanGuest`` from a router payload."""
        return cls(
            ssid=decode_b64(get_str(data, "ssid")),
            password=decode_b64(get_str(data, "password")),
            enable=get_bool(data, "enable"),
            vlan_id=get_int(data, "vlan_id") if "vlan_id" in data else None,
            need_set_vlan=(get_bool(data, "need_set_vlan") if "need_set_vlan" in data else None),
        )


@dataclass(frozen=True)
class WlanBackhaul:
    """Mesh backhaul channel for a band."""

    channel: int

    @classmethod
    def from_api(cls, data: JsonObject) -> WlanBackhaul:
        """Build ``WlanBackhaul`` from a router payload."""
        return cls(channel=get_int(data, "channel"))


@dataclass(frozen=True)
class WlanBand:
    """All SSID configurations for a single radio band."""

    host: WlanHost
    guest: WlanGuest
    backhaul: WlanBackhaul

    @classmethod
    def from_api(cls, data: JsonObject) -> WlanBand:
        """Build ``WlanBand`` from a router payload."""
        return cls(
            host=WlanHost.from_api(get_object(data, "host")),
            guest=WlanGuest.from_api(get_object(data, "guest")),
            backhaul=WlanBackhaul.from_api(get_object(data, "backhaul")),
        )


@dataclass(frozen=True)
class IotHost:
    """IoT-dedicated SSID configuration."""

    ssid: str
    password: str
    encryption_mode: str
    enable: bool
    enable_2g: bool
    enable_5g: bool

    @classmethod
    def from_api(cls, data: JsonObject) -> IotHost:
        """Build ``IotHost`` from a router payload."""
        return cls(
            ssid=decode_b64(get_str(data, "ssid")),
            password=decode_b64(get_str(data, "password")),
            encryption_mode=get_str(data, "encryption_mode"),
            enable=get_bool(data, "enable"),
            enable_2g=get_bool(data, "enable_2g"),
            enable_5g=get_bool(data, "enable_5g"),
        )


@dataclass(frozen=True)
class MloHost:
    """Multi-Link Operation host configuration."""

    ssid: str
    password: str
    enable: bool
    band: tuple[str, ...]
    enable_hide_ssid: bool

    @classmethod
    def from_api(cls, data: JsonObject) -> MloHost:
        """Build ``MloHost`` from a router payload."""
        return cls(
            ssid=decode_b64(get_str(data, "ssid")),
            password=decode_b64(get_str(data, "password")),
            enable=get_bool(data, "enable"),
            band=get_str_tuple(data, "band"),
            enable_hide_ssid=get_bool(data, "enable_hide_ssid"),
        )


@dataclass(frozen=True)
class WlanConfig:
    """Top-level Wi-Fi configuration returned by ``admin/wireless?form=wlan``."""

    band2_4: WlanBand
    band5_1: WlanBand
    band6: WlanBand
    iot_host: IotHost
    mlo_host: MloHost
    is_eg: bool = False

    @classmethod
    def from_api(cls, data: JsonObject) -> WlanConfig:
        """Build ``WlanConfig`` from a router payload."""
        return cls(
            band2_4=WlanBand.from_api(get_object(data, "band2_4")),
            band5_1=WlanBand.from_api(get_object(data, "band5_1")),
            band6=WlanBand.from_api(get_object(data, "band6")),
            iot_host=IotHost.from_api(get_object(get_object(data, "iot"), "host")),
            mlo_host=MloHost.from_api(get_object(get_object(data, "mlo"), "host")),
            is_eg=get_bool(data, "is_eg"),
        )
