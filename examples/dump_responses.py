#!/usr/bin/env python3
"""
Chama cada método público do SDK e salva o resultado em docs/api-responses/.

Uso:
    uv run examples/dump_responses.py
"""

import dataclasses
import json
import pathlib
import sys

_OUT = pathlib.Path(__file__).parent.parent / "docs" / "api-responses"


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


def _save(name: str, data: object) -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    path = _OUT / f"{name}.json"

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
    print(f"  salvo: {path.relative_to(pathlib.Path(__file__).parent.parent)}")


def main() -> None:
    env = _load_env()
    host = env.get("DECO_HOST", "192.168.5.1")
    username = env.get("DECO_USERNAME", "admin")
    password = env.get("DECO_PASSWORD", "")

    if not password:
        print("Erro: DECO_PASSWORD não definido em .env")
        sys.exit(1)

    from tplink_deco_api import DecoClient

    with DecoClient(host, username, password) as deco:
        _save("login", deco.login())
        _save("device_list", deco.get_device_list())
        _save("device_mode", deco.get_device_mode())
        _save("wlan_config", deco.get_wlan_config())
        _save("performance", deco.get_performance())
        _save("client_list", deco.get_client_list())

    print(
        f"\nConcluído. {len(list(_OUT.glob('*.json')))} arquivos em docs/api-responses/"
    )


if __name__ == "__main__":
    main()
