#!/usr/bin/env python3
"""
Uso:
    uv run examples/clients.py
    uv run examples/clients.py --host 192.168.5.1 --user admin --password SUA_SENHA
    uv run examples/clients.py --deco DC:EF:09:AA:BB:CC
"""

import argparse
import pathlib
import sys


def _load_env() -> dict[str, str]:
    env_file = pathlib.Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip()
    return values


def _parse_args() -> argparse.Namespace:
    env = _load_env()
    parser = argparse.ArgumentParser(description="Lista clientes conectados ao Deco")
    parser.add_argument("--host", default=env.get("DECO_HOST", "192.168.5.1"))
    parser.add_argument("--user", default=env.get("DECO_USERNAME", "admin"))
    parser.add_argument("--password", default=env.get("DECO_PASSWORD", ""))
    parser.add_argument(
        "--deco",
        default="default",
        metavar="MAC",
        help="MAC do nó Deco (padrão: todos)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if not args.password:
        print(
            "Erro: senha não fornecida. Use --password ou defina DECO_PASSWORD no .env"
        )
        sys.exit(1)

    from tplink_deco_api import DecoClient
    from tplink_deco_api.models import ClientDevice

    with DecoClient(args.host, args.user, args.password) as deco:
        clients: list[ClientDevice] = deco.get_client_list(args.deco)

    if not clients:
        print("Nenhum cliente conectado.")
        return

    col_mac = max(len(c.mac) for c in clients)
    col_ip = max(len(c.ip) for c in clients)
    col_name = max(len(c.name) for c in clients)

    header = f"{'MAC':<{col_mac}}  {'IP':<{col_ip}}  {'NOME':<{col_name}}  TIPO          BANDA         ONLINE"
    print(header)
    print("-" * len(header))

    for c in sorted(clients, key=lambda x: x.ip):
        online = "sim" if c.online else "não"
        print(
            f"{c.mac:<{col_mac}}  "
            f"{c.ip:<{col_ip}}  "
            f"{c.name:<{col_name}}  "
            f"{c.client_type:<13} "
            f"{c.connection_type:<13} "
            f"{online}"
        )

    print(f"\nTotal: {len(clients)} cliente(s)")


if __name__ == "__main__":
    main()
