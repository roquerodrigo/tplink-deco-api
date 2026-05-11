from dataclasses import dataclass
from typing import Any

from ._utils import decode_b64


@dataclass(frozen=True)
class WlanHost:
    ssid: str
    password: str
    channel: int
    enable: bool
    mode: str
    channel_width: str
    enable_hide_ssid: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "WlanHost":
        return cls(
            ssid=decode_b64(data.get("ssid", "")),
            password=decode_b64(data.get("password", "")),
            channel=int(data.get("channel", 0)),
            enable=bool(data.get("enable", False)),
            mode=data.get("mode", ""),
            channel_width=data.get("channel_width", ""),
            enable_hide_ssid=bool(data.get("enable_hide_ssid", False)),
        )


@dataclass(frozen=True)
class WlanGuest:
    ssid: str
    password: str
    enable: bool
    vlan_id: int | None = None
    need_set_vlan: bool | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "WlanGuest":
        return cls(
            ssid=decode_b64(data.get("ssid", "")),
            password=decode_b64(data.get("password", "")),
            enable=bool(data.get("enable", False)),
            vlan_id=int(data["vlan_id"]) if "vlan_id" in data else None,
            need_set_vlan=bool(data["need_set_vlan"])
            if "need_set_vlan" in data
            else None,
        )


@dataclass(frozen=True)
class WlanBackhaul:
    channel: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "WlanBackhaul":
        return cls(channel=int(data.get("channel", 0)))


@dataclass(frozen=True)
class WlanBand:
    host: WlanHost
    guest: WlanGuest
    backhaul: WlanBackhaul

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "WlanBand":
        return cls(
            host=WlanHost.from_api(data.get("host", {})),
            guest=WlanGuest.from_api(data.get("guest", {})),
            backhaul=WlanBackhaul.from_api(data.get("backhaul", {})),
        )


@dataclass(frozen=True)
class IotHost:
    ssid: str
    password: str
    encryption_mode: str
    enable: bool
    enable_2g: bool
    enable_5g: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "IotHost":
        return cls(
            ssid=decode_b64(data.get("ssid", "")),
            password=decode_b64(data.get("password", "")),
            encryption_mode=data.get("encryption_mode", ""),
            enable=bool(data.get("enable", False)),
            enable_2g=bool(data.get("enable_2g", False)),
            enable_5g=bool(data.get("enable_5g", False)),
        )


@dataclass(frozen=True)
class MloHost:
    ssid: str
    password: str
    enable: bool
    band: tuple[str, ...]
    enable_hide_ssid: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "MloHost":
        return cls(
            ssid=decode_b64(data.get("ssid", "")),
            password=decode_b64(data.get("password", "")),
            enable=bool(data.get("enable", False)),
            band=tuple(data.get("band", [])),
            enable_hide_ssid=bool(data.get("enable_hide_ssid", False)),
        )


@dataclass(frozen=True)
class WlanConfig:
    band2_4: WlanBand
    band5_1: WlanBand
    band6: WlanBand
    iot_host: IotHost
    mlo_host: MloHost
    is_eg: bool = False

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "WlanConfig":
        return cls(
            band2_4=WlanBand.from_api(data.get("band2_4", {})),
            band5_1=WlanBand.from_api(data.get("band5_1", {})),
            band6=WlanBand.from_api(data.get("band6", {})),
            iot_host=IotHost.from_api(data.get("iot", {}).get("host", {})),
            mlo_host=MloHost.from_api(data.get("mlo", {}).get("host", {})),
            is_eg=bool(data.get("is_eg", False)),
        )
