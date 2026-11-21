"""Discovery of which documented read endpoints the connected model serves."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ..exceptions import ApiError, AuthenticationError, DecoError, TransportError
from ..models import EndpointCapability
from ._read_endpoints import READ_ENDPOINTS

if TYPE_CHECKING:
    from .._json import JsonValue
    from ..models import CapabilityStatus
    from ._request import RawRequestSender

_HTTP_NOT_FOUND = 404


class CapabilityService:
    """Probes every documented read form and reports how the router answers."""

    def __init__(self, send: RawRequestSender) -> None:
        self._send = send

    def probe(self, interval: float = 0.15) -> list[EndpointCapability]:
        """Send each documented read once, ``interval`` seconds apart.

        Only read operations are sent, so the router's state never changes.
        On a single gateway it takes under a minute; much shorter intervals
        make the firmware start rejecting requests, which skews the result.
        """
        capabilities: list[EndpointCapability] = []
        for index, (path, form, operation) in enumerate(READ_ENDPOINTS):
            if index and interval > 0:
                time.sleep(interval)
            capabilities.append(self._probe(path, form, operation))
        return capabilities

    def _probe(self, path: str, form: str, operation: str) -> EndpointCapability:
        data: dict[str, JsonValue] = {"operation": operation, "params": {"device_mac": "default"}}
        try:
            result = self._send(path, form, data)
        except AuthenticationError:
            raise
        except TransportError as exc:
            if exc.status_code == _HTTP_NOT_FOUND:
                return EndpointCapability(path, form, operation, "absent", "HTTP 404")
            detail = f"HTTP {exc.status_code}" if exc.status_code else str(exc)
            return EndpointCapability(path, form, operation, "error", detail)
        except ApiError as exc:
            return EndpointCapability(
                path, form, operation, "error", f"error_code={exc.error_code}"
            )
        except (DecoError, ValueError) as exc:
            return EndpointCapability(path, form, operation, "error", str(exc))
        status: CapabilityStatus = "ok" if result else "empty"
        return EndpointCapability(path, form, operation, status)
