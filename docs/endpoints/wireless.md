# Wi-Fi — bands / guest / IoT / MLO / optimization

Endpoint: **`/admin/wireless`** (web + app). Auto-channel optimization lives at a
separate endpoint, **`/admin/network_optimize`** (app). All forms use the
[encrypted envelope](../protocol/transport-and-dispatch.md).

SSID and password fields are **base64** in both directions.

Related: [network.md](./network.md) (WAN/LAN, guest VLAN), [device.md](./device.md)
(node placement / `signal_level_list`), the index [README.md](./README.md).

---

## Forms

| Form | Operations | By | Purpose |
|------|-----------|-----|---------|
| `wlan` | read, write | both | Full per-band SSID config (host / guest / backhaul, IoT, MLO). |
| `operation_mode` | read/write | both | Wi-Fi working mode. |
| `bridge` | read | both | Bridge/backhaul status. |
| `check` | check | both | Node-placement / online check (Wi-Fi location status). |
| `ieee80211r` | read/write | both | 802.11r fast roaming (`enable`). |
| `beamforming` | read/write | both | Beamforming toggle (`enable`). |
| `bandwidth_enhance` | read/write | both | 160 MHz enable (`enable_ht160`). |
| `bandwidth_switch` | read/write | app | 160/240/320 MHz switching + support probe. |
| `power` | read/write | both | Transmit power per band + DFS support. |
| `smart_antenna` | read/write | app | Antenna coverage pattern (`coverage_type`). |
| `wifi_schedule` | read/write | app | Scheduled Wi-Fi on/off. |
| `ofdma` | read/write | app | OFDMA toggle (`enable`, `mode`). |
| `mlo_network` | read/write | app | Multi-Link Operation SSID. |
| `backhaul_optimization` | read/write | app | Backhaul-band optimization (`band2_4.mode`). |
| `get_support` | read | app | Wi-Fi capability probe (MLO bands, 6 GHz, model). |
| `acs_optimize` ¹ | read, write | app | Auto channel selection (scan / apply). |
| `acs_filter_macs` ¹ | get | app | MACs excluded from the ACS scan. |

> ¹ Served by `/admin/network_optimize`, **not** `/admin/wireless`. Listed here
> because it drives channel selection; see [`network_optimize`](#adminnetwork_optimize) below.

---

## `wlan`

**read** → `{ "operation": "read" }` (SDK `get_wlan_config` → `WlanConfig`).

Result carries one object per band the hardware exposes — `band2_4`, `band5_1`,
`band5_2`, `band6`, `band6_2` — plus `iot`, `mlo` and `is_eg`. Each band object
has `host`, `guest` and `backhaul`. Sample response:
[`../api-responses/wlan_config.json`](../api-responses/wlan_config.json).

`band.host`:

| Field | Meaning |
|-------|---------|
| `ssid` | Primary SSID (base64). |
| `password` | Pre-shared key (base64). |
| `enable` | Radio / SSID on. |
| `mode` | PHY mode (`11ng`, `11ac`, `11ax`, …). |
| `channel` / `auto_channel` | Current channel; `auto_channel` = auto-select. |
| `channel_width` | Bandwidth (`HT20`, `HT40`, `HT80`, `HT160`, …). |
| `support_channel` / `support_bandwidth` | Allowed values (app also returns `channels` / `bandwidths` lists). |
| `enable_hide_ssid` | Hide SSID broadcast. |
| `host_isolation` | Client isolation (app). |

`band.guest`:

| Field | Meaning |
|-------|---------|
| `ssid` / `password` | Guest SSID / key (base64). |
| `enable` | Guest network on. |
| `encryption` / `encryption_mode` | `none`, `wpa2`, `wpa3`, `wpa3+wpa2`. |
| `vlan_id` / `vlan_enable` / `need_set_vlan` | Guest VLAN tagging (rejects the WAN VLAN id). |
| `access_duration` / `start_time` / `remain_time` | Timed guest access. |
| `bandwidth_limit` | `bw_limit_enable`, `bw_limit_down` (`downstream_bandwidth`), `bw_limit_up` (`upstream_bandwidth`). |

`band.backhaul`: `channel` — mesh backhaul channel.

`iot.host` (SDK `IotHost`): `ssid`, `password`, `encryption_mode` (`wpa2+wpa`),
`enable`, `enable_2g`, `enable_5g`.

`mlo.host` (SDK `MloHost`): `ssid`, `password`, `enable`, `band` (list of
`band2`/`band5`/`band5_2`/`band6`/`band6_2`), `enable_hide_ssid`.

Top level: `is_eg` (EasyMesh / special-ID flavour flag).

**write** → apply per-band config; each key is optional and only the supplied
sub-objects are changed:

```json
{
  "operation": "write",
  "params": {
    "band2_4": { "host": { "enable_2g": true, "ssid": "<b64>", "password": "<b64>",
                           "encryption": "wpa2", "channel": "auto",
                           "channel_width": "HT40", "hidessid": false },
                 "guest": { "enable": true, "ssid": "<b64>", "password": "<b64>" } },
    "iot":  { "host": { "enable": true, "ssid": "<b64>", "password": "<b64>" } },
    "mlo":  { "host": { "enable": true, "band": ["band5", "band6"] } }
  }
}
```

Write params per host: `enable_2g` / `enable_5g` / `enable_5g2` / `enable_6g` /
`enable_6g2`, `ssid`, `password`, `encryption`, `hidessid`, `mode`, `channel`,
`channel_width`, `host_isolation`. Disabling the 2.4 GHz and 5 GHz host radios
at once is rejected ("2.4G and 5G of main network cannot be closed at the same
time").

SDK: `deco.wireless.set_wlan(band, *, guest=False, ssid=None, password=None, enable=None)`
writes `params.<band>.host` (enable key from the table above) or
`params.<band>.guest` (`enable`). Only the passed fields are sent; the
payload follows this section and has not been checked on hardware.

## `power`

**read** → `{ "operation": "read", "params": { "device_mac": "default" } }`
(SDK `get_wireless_power` → `WirelessPower`). Gated by `is_txpower_support`.

| Field | Meaning |
|-------|---------|
| `support_dfs` | 5 GHz DFS supported (SDK `WirelessPower.support_dfs`). |
| `band2_4` / `band5_1` / `band5_2` | Per-band transmit-power level. |

**write** — set `txpower` per band; params are `band2_4` / `band5_1` /
`band5_2`.

## `operation_mode`

**read / write** — reads/sets the Wi-Fi working `mode`. Distinct from `bridge`,
which reports backhaul status only. SDK: `deco.wireless.get_operation_mode()`.

## Single-flag reads

Seen on a Deco X50-5G (firmware 1.1.3):

| Form | Result | SDK |
|------|--------|-----|
| `ieee80211r` | `{ "enable": false }` | `deco.wireless.get_fast_roaming()` |
| `bandwidth_enhance` | `{ "enable_ht160": true }` | `deco.wireless.get_ht160_enabled()` |
| `operation_mode` | `{ "mode": "AP" }` | `deco.wireless.get_operation_mode()` |
| `bridge` | `{ "support_plc": false, "location": "good", "status": "getting" }` | `deco.wireless.get_bridge()` → `WirelessBridge` |

## `wifi_schedule` (app)

**read / write** — turn Wi-Fi radios off on a schedule.

| Field | Meaning |
|-------|---------|
| `enable` | Schedule active. |
| `begin_time` / `end_time` | Schedule window. |
| `enable_band2_4` | Schedule the 2.4 GHz radio separately. |
| `user_set` / `has_set_wifi_schedule` | Whether the user has configured it. |

Newer Deco devices may not support this ("New Deco device does not support
wifi_schedule, disable it.").

## `mlo_network` (app)

**read / write** — MLO SSID. Gated by `is_mlo_support` / `is_mlo_band_support`.

| Field | Meaning |
|-------|---------|
| `enable` | MLO SSID on. |
| `ssid` / `password` | SSID / key (base64). |
| `encryption` / `encryption_mode` | `wpa3`. |
| `hidessid` / `enable_hide_ssid` | Hide SSID broadcast. |
| `band` | Member bands, subset of `band2` / `band5` / `band5_2` / `band6` / `band6_2`. |

## `/admin/network_optimize`

App-only endpoint for auto channel selection (ACS).

**`acs_optimize` read** → `{ "operation": "read" }` — best-channel scan result:

| Field | Meaning |
|-------|---------|
| `need_optimize` | Whether a better channel was found. |
| `scan_count` / `optimize_count` | Scan / applied-optimization counters. |
| `optimize_item` | Per-band recommendation (`band2_4`→`channel_2g`, `band5_1`→`channel_5g`, `band5_2`→`channel_5g_2`, `band6`→`channel_6g`). |
| `optimize_time` | Last-optimization timestamp. |

**`acs_optimize` write** — trigger the scan / apply the best channel. Runs are
serialized so scans and applies don't overlap.

**`acs_filter_macs` get** — MACs excluded from the ACS scan.

---

## Notes

- Band suffixes: `band2_4` (2.4 GHz), `band5_1` (5 GHz-1), `band5_2` (5 GHz-2),
  `band6` (6 GHz), `band6_2` (6 GHz-2). Only bands present on the hardware are
  returned; the SDK `WlanConfig` currently maps `band2_4`, `band5_1`, `band6`,
  plus `iot_host` and `mlo_host`.
- Capability gates decide which forms/fields exist per model:
  `is_band_5g2_support`, `is_band_6g_support`, `is_band_6g2_support`,
  `is_mlo_support`, `is_iot_support`, `is_wpa3_support`, `is_ofdma_support`,
  `is_ht240_support`, `is_txpower_support`.
- `bandwidth_enhance` toggles 160 MHz (`enable_ht160`); `bandwidth_switch` (app)
  drives the richer 160/240/320 MHz switching.
- `smart_antenna` `coverage_type` is `auto` / `horizontal` / `vertical`.
- Per-band signal level (SDK `SignalLevel`: `band2_4` / `band5` / `band6`) is
  served by the **device** endpoint (`signal_level_list`), not here — see
  [device.md](./device.md).
- Guest-network VLAN tagging overlaps with [network.md](./network.md)
  (`vlan` / `wifi_network`); the guest VLAN id must differ from the WAN VLAN.
