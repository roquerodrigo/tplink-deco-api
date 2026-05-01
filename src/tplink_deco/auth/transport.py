import json
import re
import urllib.error
import urllib.request

from ..exceptions.transport import TransportError

_COOKIE_RE = re.compile(r"(sysauth=[a-f0-9]+)")


class HttpTransport:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._cookie: str | None = None

    def post_json(self, url: str, body: dict) -> dict:
        """POST com corpo JSON (endpoints sem criptografia)."""
        return self._post(url, json.dumps(body).encode())

    def post_form(self, url: str, body: str) -> dict:
        """POST com corpo sign=...&data=... (endpoints cifrados)."""
        return self._post(url, body.encode())

    def _post(self, url: str, data: bytes) -> dict:
        headers = {"Content-Type": "application/json"}
        if self._cookie:
            headers["Cookie"] = self._cookie
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                self._capture_cookie(resp)
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise TransportError(str(exc), status_code=exc.code) from exc
        except urllib.error.URLError as exc:
            raise TransportError(str(exc)) from exc

    def _capture_cookie(self, resp) -> None:
        for header, value in resp.headers.items():
            if header.lower() == "set-cookie":
                match = _COOKIE_RE.search(value)
                if match:
                    self._cookie = match.group(1)
                    break
