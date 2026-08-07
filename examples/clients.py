#!/usr/bin/env python3
"""List clients connected to a TP-Link Deco mesh.

Usage::

    uv run examples/clients.py
    uv run examples/clients.py --host 192.168.0.1 --user admin --password YOUR_PASSWORD
    uv run examples/clients.py --deco DC:EF:09:AA:BB:CC
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from tplink_deco_api._env import load_env


def _parse_args() -> argparse.Namespace:
    env = load_env(pathlib.Path(__file__).parent.parent / ".env")
    parser = argparse.ArgumentParser(description="List clients connected to a Deco mesh")
    parser.add_argument("--host", default=env.get("DECO_HOST", "192.168.0.1"))
    parser.add_argument("--user", default=env.get("DECO_USERNAME", "admin"))
    parser.add_argument("--password", default=env.get("DECO_PASSWORD", ""))
    parser.add_argument(
        "--deco",
        default="default",
        metavar="MAC",
        help="MAC of the target Deco node (default: all nodes)",
    )
    return parser.parse_args()


def main() -> None:
    """Print a table of every client connected to the mesh."""
    args = _parse_args()

    if not args.password:
        print("Error: password not provided. Use --password or set DECO_PASSWORD in .env")
        sys.exit(1)

    from tplink_deco_api import DecoClient

    with DecoClient(args.host, args.user, args.password) as deco:
        clients = deco.get_client_list(args.deco)

    if not clients:
        print("No clients connected.")
        return

    col_mac = max(len(c.mac) for c in clients)
    col_ip = max(len(c.ip) for c in clients)
    col_name = max(len(c.name) for c in clients)

    header = (
        f"{'MAC':<{col_mac}}  {'IP':<{col_ip}}  {'NAME':<{col_name}}  "
        "TYPE          BAND          ONLINE"
    )
    print(header)
    print("-" * len(header))

    for c in sorted(clients, key=lambda x: x.ip):
        online = "yes" if c.online else "no"
        print(
            f"{c.mac:<{col_mac}}  "
            f"{c.ip:<{col_ip}}  "
            f"{c.name:<{col_name}}  "
            f"{c.client_type:<13} "
            f"{c.connection_type:<13} "
            f"{online}"
        )

    print(f"\nTotal: {len(clients)} client(s)")


if __name__ == "__main__":
    main()
