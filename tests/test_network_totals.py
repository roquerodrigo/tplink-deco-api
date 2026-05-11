from tplink_deco_api import NetworkTotals
from tplink_deco_api.models import ClientDevice


def _make_client(up: int, down: int) -> ClientDevice:
    return ClientDevice(
        mac="AA:BB:CC:DD:EE:FF",
        ip="192.168.1.10",
        name="test",
        up_speed=up,
        down_speed=down,
        wire_type="",
        connection_type="",
        space_id="",
        access_host="",
        interface="",
        client_type="",
        owner_id="",
        remain_time=0,
        online=True,
        client_mesh=False,
        enable_priority=False,
    )


def test_from_clients_empty():
    totals = NetworkTotals.from_clients([])
    assert totals.up_speed == 0
    assert totals.down_speed == 0


def test_from_clients_sums_all():
    clients = [
        _make_client(up=100, down=200),
        _make_client(up=50, down=75),
        _make_client(up=0, down=10),
    ]
    totals = NetworkTotals.from_clients(clients)
    assert totals.up_speed == 150
    assert totals.down_speed == 285


def test_from_clients_accepts_generator():
    clients = (_make_client(up=i, down=i * 2) for i in range(5))
    totals = NetworkTotals.from_clients(clients)
    assert totals.up_speed == 0 + 1 + 2 + 3 + 4
    assert totals.down_speed == (0 + 1 + 2 + 3 + 4) * 2
