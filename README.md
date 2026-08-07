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

### Session

| Method | Returns |
|--------|---------|
| `login()` | `LoginResult` |
| `logout()` | `None` |
| `is_authenticated()` | `bool` |

### Typed queries

| Method | Returns |
|--------|---------|
| `get_device_list()` | `list[Device]` |
| `get_device_mode()` | `DeviceMode` |
| `get_wlan_config()` | `WlanConfig` |
| `get_performance()` | `Performance` |
| `get_client_list(deco_mac?)` | `list[ClientDevice]` |
| `get_client_totals(deco_mac?)` | `NetworkTotals` |
| `get_internet_status()` | `InternetStatus` |
| `get_wan_info(device_mac?)` | `WanInfo` |
| `get_dsl_status(device_mac?)` | `DslStatus` |
| `get_wireless_power(device_mac?)` | `WirelessPower` |
| `get_time_settings(device_mac?)` | `TimeSettings` |
| `get_log_types()` | `list[LogType]` |

### Raw access

`request(path, form, data)` and `request_list(path, form, data)` send an
authenticated, encrypted request to any endpoint and return the decrypted
`result` (as an object or a list respectively). Use them for the endpoints
that have no typed wrapper yet — the full catalogue is documented in
[`docs/endpoints/`](./docs/endpoints/README.md).

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

## License

[MIT](./LICENSE)
