"""Services grouped by the router feature they read and change."""

from __future__ import annotations

from .address_reservation_service import AddressReservationService
from .capability_service import CapabilityService
from .client_service import ClientService
from .device_service import DeviceService
from .network_service import NetworkService
from .wireless_service import WirelessService

__all__ = [
    "AddressReservationService",
    "CapabilityService",
    "ClientService",
    "DeviceService",
    "NetworkService",
    "WirelessService",
]
