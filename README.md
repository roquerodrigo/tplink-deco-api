# tplink-deco-api

[![CI](https://github.com/roquerodrigo/tplink-deco-api/actions/workflows/ci.yml/badge.svg)](https://github.com/roquerodrigo/tplink-deco-api/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tplink-deco-api)](https://pypi.org/project/tplink-deco-api/)

Python SDK for controlling **TP-Link Deco** mesh Wi-Fi routers via the internal HTTP API.

## Installation

```bash
pip install tplink-deco-api
```

## Usage

```python
from tplink_deco_api import DecoClient

with DecoClient("192.168.68.1", "admin", "your-password") as deco:
    for client in deco.get_client_list():
        print(client.name, client.ip, client.connection_type)
```

## Available methods

| Method | Returns |
|--------|---------|
| `login()` | `LoginResult` |
| `get_device_list()` | `list[Device]` |
| `get_device_mode()` | `DeviceMode` |
| `get_wlan_config()` | `WlanConfig` |
| `get_performance()` | `Performance` |
| `get_client_list(deco_mac?)` | `list[ClientDevice]` |

## Models

Every method returns typed dataclasses — no generic dictionaries.

```python
client.mac              # "AA:BB:CC:DD:EE:FF"
client.name             # "MacBook Pro"
client.ip               # "192.168.68.10"
client.connection_type  # "band6"
client.online           # True

device.device_model     # "BE65"
device.software_ver     # "1.2.10 Build 20251229"

wlan.band2_4.host.ssid      # "My Network"
wlan.band2_4.guest.password # "guest-password"

perf.cpu_usage  # 0.03
perf.mem_usage  # 0.42
```

## Requirements

- Python 3.11+
- TP-Link Deco router reachable on the local network
