"""URL builders for the router's CGI entry point."""

from __future__ import annotations


def login_url(host: str, form: str) -> str:
    """Return the unauthenticated ``/login`` URL for the given ``form``."""
    return f"https://{host}/cgi-bin/luci/;stok=/login?form={form}"


def admin_url(host: str, stok: str, path: str, form: str) -> str:
    """Return the authenticated admin URL for ``path`` + ``form``."""
    return f"https://{host}/cgi-bin/luci/;stok={stok}/{path}?form={form}"
