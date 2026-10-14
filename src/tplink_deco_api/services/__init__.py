"""Write-capable services grouped by the router feature they manage."""

from __future__ import annotations

from .address_reservation_service import AddressReservationService
from .client_service import ClientService

__all__ = ["AddressReservationService", "ClientService"]
