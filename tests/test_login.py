"""
Teste de integração — requer roteador acessível e credenciais em .env

Execute:
    uv run pytest tests/test_login.py -v -s
"""

import pathlib

import pytest

from tplink_deco_api import AuthenticationError, DecoClient
from tplink_deco_api.models import (
    ClientDevice,
    Device,
    DeviceMode,
    Performance,
    WlanConfig,
)


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


_ENV = _load_env()
_HOST = _ENV.get("DECO_HOST", "192.168.5.1")
_USERNAME = _ENV.get("DECO_USERNAME", "admin")
_PASSWORD = _ENV.get("DECO_PASSWORD", "")

pytestmark = pytest.mark.skipif(
    not _PASSWORD,
    reason="DECO_PASSWORD não definido em .env",
)


def test_login_retorna_stok():
    client = DecoClient(_HOST, _USERNAME, _PASSWORD)
    result = client.login()

    print(f"\n  stok={result.stok[:16]}...")
    print(f"  usr_lvl={result.usr_lvl}")

    assert result.stok
    assert isinstance(result.usr_lvl, int)


def test_login_credenciais_erradas():
    client = DecoClient(_HOST, _USERNAME, "senha_errada_xyz_123")
    with pytest.raises((AuthenticationError, Exception)):
        client.login()


def test_context_manager():
    with DecoClient(_HOST, _USERNAME, _PASSWORD) as deco:
        assert deco.is_authenticated()
    assert not deco.is_authenticated()


def test_get_device_mode():
    with DecoClient(_HOST, _USERNAME, _PASSWORD) as deco:
        mode = deco.get_device_mode()
        print(f"\n  workmode={mode.workmode!r}")
        print(f"  sysmode={mode.sysmode!r}")
        print(f"  region={mode.region!r}")
        assert isinstance(mode, DeviceMode)
        assert isinstance(mode.workmode, str)
        assert isinstance(mode.sysmode, str)


def test_get_wlan_config():
    with DecoClient(_HOST, _USERNAME, _PASSWORD) as deco:
        wlan = deco.get_wlan_config()
        print(f"\n  band2_4 ssid={wlan.band2_4.host.ssid!r}")
        print(f"  band5_1 channel={wlan.band5_1.host.channel}")
        print(f"  band6 channel={wlan.band6.host.channel}")
        assert isinstance(wlan, WlanConfig)
        assert isinstance(wlan.band2_4.host.channel, int)
        assert isinstance(wlan.band6.guest.enable, bool)


def test_get_device_list():
    with DecoClient(_HOST, _USERNAME, _PASSWORD) as deco:
        devices = deco.get_device_list()
        print(f"\n  devices={[d.mac for d in devices]}")
        assert isinstance(devices, list)
        assert all(isinstance(d, Device) for d in devices)
        if devices:
            assert isinstance(devices[0].signal_level.band2_4, str)


def test_get_performance():
    with DecoClient(_HOST, _USERNAME, _PASSWORD) as deco:
        perf = deco.get_performance()
        print(f"\n  cpu={perf.cpu_usage:.0%}  mem={perf.mem_usage:.0%}")
        assert isinstance(perf, Performance)
        assert 0.0 <= perf.cpu_usage <= 1.0
        assert 0.0 <= perf.mem_usage <= 1.0


def test_get_client_list():
    with DecoClient(_HOST, _USERNAME, _PASSWORD) as deco:
        clients = deco.get_client_list()
        print(f"\n  clients={[c.mac for c in clients]}")
        assert isinstance(clients, list)
        assert all(isinstance(c, ClientDevice) for c in clients)
