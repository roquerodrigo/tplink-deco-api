#!/usr/bin/env python3
"""Call every public SDK method and dump the result into ``docs/api-responses/``.

Usage::

    uv run examples/dump_responses.py
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import sys

from tplink_deco_api._env import load_env

_OUT = pathlib.Path(__file__).parent.parent / "docs" / "api-responses"


def _save(name: str, data: object) -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    path = _OUT / f"{name}.json"

    serializable: object
    if dataclasses.is_dataclass(data) and not isinstance(data, type):
        serializable = dataclasses.asdict(data)
    elif isinstance(data, list):
        serializable = [
            dataclasses.asdict(item)
            if dataclasses.is_dataclass(item) and not isinstance(item, type)
            else item
            for item in data
        ]
    else:
        serializable = data

    path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False))
    print(f"  saved: {path.relative_to(pathlib.Path(__file__).parent.parent)}")


def main() -> None:
    """Log in, call every typed query and save each response as JSON."""
    env = load_env(pathlib.Path(__file__).parent.parent / ".env")
    host = env.get("DECO_HOST", "192.168.0.1")
    username = env.get("DECO_USERNAME", "admin")
    password = env.get("DECO_PASSWORD", "")

    if not password:
        print("Error: DECO_PASSWORD not set in .env")
        sys.exit(1)

    from tplink_deco_api import DecoClient

    with DecoClient(host, username, password) as deco:
        _save("login", deco.login())
        _save("device_list", deco.get_device_list())
        _save("device_mode", deco.get_device_mode())
        _save("wlan_config", deco.get_wlan_config())
        _save("performance", deco.get_performance())
        _save("client_list", deco.get_client_list())

    print(f"\nDone. {len(list(_OUT.glob('*.json')))} files in docs/api-responses/")


if __name__ == "__main__":
    main()
