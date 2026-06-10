"""Public dataclasses returned by the SDK."""

from __future__ import annotations

from .client_device import ClientDevice
from .device import Device
from .device_mode import DeviceMode
from .dsl_status import DslStatus
from .internet_status import InternetStatus, IpStatus
from .login_result import LoginResult
from .network_totals import NetworkTotals
from .performance import Performance
from .signal_level import SignalLevel
from .wan_info import IpInfo, LanDetails, WanDetails, WanInfo
from .wlan_config import (
    IotHost,
    MloHost,
    WlanBackhaul,
    WlanBand,
    WlanConfig,
    WlanGuest,
    WlanHost,
)

__all__ = [
    "ClientDevice",
    "Device",
    "DeviceMode",
    "DslStatus",
    "InternetStatus",
    "IpInfo",
    "IpStatus",
    "IotHost",
    "LanDetails",
    "LoginResult",
    "MloHost",
    "NetworkTotals",
    "Performance",
    "SignalLevel",
    "WanDetails",
    "WanInfo",
    "WlanBackhaul",
    "WlanBand",
    "WlanConfig",
    "WlanGuest",
    "WlanHost",
]
