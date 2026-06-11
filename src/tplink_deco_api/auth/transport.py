"""Minimal HTTP transport with cookie tracking for the Deco router."""

from __future__ import annotations

import json
import logging
import re
import ssl
import urllib.error
import urllib.request
from typing import TYPE_CHECKING

from .._json import JsonObject, loads
from ..exceptions.transport import TransportError

if TYPE_CHECKING:
    from collections.abc import Mapping
    from http.client import HTTPResponse

log: logging.Logger = logging.getLogger("tplink_deco_api.transport")

_COOKIE_RE = re.compile(r"(sysauth=[a-f0-9]+)")


class HttpTransport:
    """POST JSON / form payloads to the router, tracking the ``sysauth`` cookie."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self._cookie: str | None = None
        self._ssl_ctx = ssl.create_default_context()
        self._ssl_ctx.check_hostname = False
        self._ssl_ctx.verify_mode = ssl.CERT_NONE

    def post_json(self, url: str, body: Mapping[str, str]) -> JsonObject:
        """POST ``body`` as JSON and return the parsed response."""
        return self._post(url, json.dumps(body).encode())

    def post_form(self, url: str, body: str) -> JsonObject:
        """POST a pre-serialized form body and return the parsed response."""
        return self._post(url, body.encode())

    def _post(self, url: str, data: bytes) -> JsonObject:
        headers = {"Content-Type": "application/json"}
        if self._cookie:
            headers["Cookie"] = self._cookie
        req = urllib.request.Request(url, data=data, headers=headers)
        log.debug("POST %s (%d bytes)", url, len(data))
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ssl_ctx) as resp:
                self._capture_cookie(resp)
                return loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise TransportError(
                f"Failed to POST {url}: HTTP {exc.code}",
                status_code=exc.code,
            ) from exc
        except urllib.error.URLError as exc:
            raise TransportError(f"Failed to POST {url}: {exc.reason}") from exc

    def _capture_cookie(self, resp: HTTPResponse) -> None:
        for header, value in resp.headers.items():
            if header.lower() == "set-cookie":
                match = _COOKIE_RE.search(value)
                if match:
                    self._cookie = match.group(1)
                    break
