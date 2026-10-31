"""Public dataclasses returned by the SDK."""

from __future__ import annotations

from .address_reservation import AddressReservation, AddressReservationTable
from .blocked_client import BlockedClient
from .client_device import ClientDevice
from .device import Device
from .device_mode import DeviceMode
from .dsl_status import DslStatus
from .internet_status import InternetStatus, IpStatus
from .log_type import LogType
from .login_result import LoginResult
from .network_totals import NetworkTotals
from .performance import Performance
from .signal_level import SignalLevel
from .system_log_page import SystemLogEntry, SystemLogPage
from .time_settings import TimeSettings
from .wan_info import IpInfo, LanDetails, WanDetails, WanInfo
from .wireless_power import WirelessPower
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
    "AddressReservation",
    "AddressReservationTable",
    "BlockedClient",
    "ClientDevice",
    "Device",
    "DeviceMode",
    "DslStatus",
    "InternetStatus",
    "IotHost",
    "IpInfo",
    "IpStatus",
    "LanDetails",
    "LogType",
    "LoginResult",
    "MloHost",
    "NetworkTotals",
    "Performance",
    "SignalLevel",
    "SystemLogEntry",
    "SystemLogPage",
    "TimeSettings",
    "WanDetails",
    "WanInfo",
    "WirelessPower",
    "WlanBackhaul",
    "WlanBand",
    "WlanConfig",
    "WlanGuest",
    "WlanHost",
]
