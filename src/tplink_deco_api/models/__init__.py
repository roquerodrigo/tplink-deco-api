"""Public dataclasses returned by the SDK."""

from __future__ import annotations

from .address_reservation import AddressReservation, AddressReservationTable
from .blocked_client import BlockedClient
from .client_device import ClientDevice
from .device import Device
from .device_mode import DeviceMode
from .dsl_status import DslStatus
from .endpoint_capability import CapabilityStatus, EndpointCapability
from .internet_status import InternetStatus, IpStatus
from .lan_ip import LanIp
from .log_type import LogType
from .login_result import LoginResult
from .mobile_status import MobileStatus
from .network_totals import NetworkTotals
from .performance import Performance
from .signal_level import SignalLevel
from .system_log_page import SystemLogEntry, SystemLogPage
from .time_settings import TimeSettings
from .wan_info import IpInfo, LanDetails, WanDetails, WanInfo
from .wireless_bridge import WirelessBridge
from .wireless_power import WirelessPower
from .wlan_config import (
    IotHost,
    MloHost,
    WlanBackhaul,
    WlanBand,
    WlanBandName,
    WlanConfig,
    WlanGuest,
    WlanHost,
)

__all__ = [
    "AddressReservation",
    "AddressReservationTable",
    "BlockedClient",
    "CapabilityStatus",
    "ClientDevice",
    "Device",
    "DeviceMode",
    "DslStatus",
    "EndpointCapability",
    "InternetStatus",
    "IotHost",
    "IpInfo",
    "IpStatus",
    "LanDetails",
    "LanIp",
    "LogType",
    "LoginResult",
    "MloHost",
    "MobileStatus",
    "NetworkTotals",
    "Performance",
    "SignalLevel",
    "SystemLogEntry",
    "SystemLogPage",
    "TimeSettings",
    "WanDetails",
    "WanInfo",
    "WirelessBridge",
    "WirelessPower",
    "WlanBackhaul",
    "WlanBand",
    "WlanBandName",
    "WlanConfig",
    "WlanGuest",
    "WlanHost",
]
