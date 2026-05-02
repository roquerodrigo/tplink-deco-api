from dataclasses import dataclass
from typing import Any

from ._utils import decode_b64, normalize_mac
from .signal_level import SignalLevel


@dataclass(frozen=True)
class Device:
    mac: str
    device_ip: str
    device_model: str
    device_type: str
    role: str
    nickname: str
    custom_nickname: str
    hardware_ver: str
    software_ver: str
    oem_id: str
    hw_id: str
    bssid_2g: str
    bssid_5g: str
    bssid_sta_2g: str
    bssid_sta_5g: str
    inet_status: str
    inet_error_msg: str
    group_status: str
    signal_level: SignalLevel
    product_level: int
    set_gateway_support: bool
    support_plc: bool
    oversized_firmware: bool
    nand_flash: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Device":
        return cls(
            mac=normalize_mac(data["mac"]),
            device_ip=data.get("device_ip", ""),
            device_model=data.get("device_model", ""),
            device_type=data.get("device_type", ""),
            role=data.get("role", ""),
            nickname=data.get("nickname", ""),
            custom_nickname=decode_b64(data.get("custom_nickname", "")),
            hardware_ver=data.get("hardware_ver", ""),
            software_ver=data.get("software_ver", ""),
            oem_id=data.get("oem_id", ""),
            hw_id=data.get("hw_id", ""),
            bssid_2g=normalize_mac(data.get("bssid_2g", "")),
            bssid_5g=normalize_mac(data.get("bssid_5g", "")),
            bssid_sta_2g=normalize_mac(data.get("bssid_sta_2g", "")),
            bssid_sta_5g=normalize_mac(data.get("bssid_sta_5g", "")),
            inet_status=data.get("inet_status", ""),
            inet_error_msg=data.get("inet_error_msg", ""),
            group_status=data.get("group_status", ""),
            signal_level=SignalLevel.from_api(data.get("signal_level", {})),
            product_level=int(data.get("product_level", 0)),
            set_gateway_support=bool(data.get("set_gateway_support", False)),
            support_plc=bool(data.get("support_plc", False)),
            oversized_firmware=bool(data.get("oversized_firmware", False)),
            nand_flash=bool(data.get("nand_flash", False)),
        )
