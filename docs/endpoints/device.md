# Device — Deco nodes, speed test & node control

Endpoint: **`/admin/device`**. Served by both the web UI and the app; app-only
forms are marked in the By column. All forms use the
[encrypted envelope](../protocol/transport-and-dispatch.md).

Reads and node-targeted writes carry the node identity in `params`
(`device_id`, or `device_mac`/`mac` for MAC-keyed forms); `"default"` /
omitted targets the gateway.

Related: [network.md](./network.md),
[eco-mode-and-time.md](./eco-mode-and-time.md) (`timesetting` / `systime` /
`eco_mode` detail), [firmware-and-upgrade.md](./firmware-and-upgrade.md),
[README.md](./README.md).

---

## Forms

| Form | Operations | By | Purpose |
|------|-----------|-----|---------|
| `device_list` | read, remove | both | Mesh node inventory; remove/unbind a node. |
| `mode` | read | web | Work mode / system mode / region (SDK `DeviceMode`). |
| `speedtest` | read, write, stop | both | Run / read / stop an internet speed test. |
| `get_server` | read, clear | both | Speed-test server list; clear stored month history. |
| `timesetting` | read, write | both | Node date / time / timezone (SDK `TimeSettings`). |
| `system` | read, write | both | Per-node system settings (nickname / location). |
| `reboot` | write | both | Reboot a node (or the answering unit). |
| `factory` | write | both | Factory reset (erase user/device/group config). |
| `gateway` | read | both | Gateway / master-role support info. |
| `mini_device_list` | read | web | Reduced node list. |
| `led` | read/write | app | LED enable + night-mode / auto-LED schedule. |
| `envar` | read/write | app | Node environment vars (`ui_language`, LED, eco status). |
| `sysmode` | read | app | System mode (`Router` / `AP` / mobile). |
| `speedinfo` | read | app | Last speed-test result snapshot. |
| `set_backup` | write | app | Mobile 4G/5G WAN backup mode. |
| `device_prefer_set` | set | app | Preferred parent node / topology. |
| `signal_level_list` | read | app | Per-node backhaul signal level. |
| `detect_mode` | read | app | WAN auto-detect mode. |
| `fixed_wan_port` | read/write | app | Fixed WAN port selection. |
| `systime` | read | app | System time snapshot. |
| `eco_mode` | read/write | app | Eco / power mode (v1) — see [eco-mode-and-time.md](./eco-mode-and-time.md). |

---

## `device_list`

**read** → `{ "operation": "read" }`

Returns every bound mesh node. SDK model: `Device` (`get_devices()`). Sample
response: [`../api-responses/device_list.json`](../api-responses/device_list.json).

| Field | Meaning |
|-------|---------|
| `mac` | Node MAC. |
| `device_ip` | LAN IP of the node. |
| `device_model` | Model (`BE65`, …). |
| `device_type` | `HOMEWIFISYSTEM`. |
| `role` | `master` / `slave`. |
| `nickname` / `custom_nickname` | Location preset / base64 custom name. |
| `hardware_ver` / `software_ver` | HW / FW version strings. |
| `oem_id` / `hw_id` | OEM and hardware identifiers. |
| `bssid_2g` / `bssid_5g` / `bssid_sta_2g` / `bssid_sta_5g` | Per-band BSSIDs. |
| `inet_status` | `online` / `offline`. |
| `inet_error_msg` | `well`, `master_unknown`, `disconnected`, … |
| `group_status` | `connected`. |
| `signal_level` | `{ band2_4, band5, band6 }`. |
| `product_level` | Numeric product tier. |
| `set_gateway_support` | Whether the node can become gateway/master. |
| `support_plc` / `oversized_firmware` / `nand_flash` | Capability flags. |

The raw payload also carries `device_id`, `parent_device_id`,
`second_parent_device_id`, `connection_type`, `speed_diagnose`, `port_count`
and `owner_transfer` (not modelled by the SDK).

**remove** → `{ "operation": "remove", "params": { "device_id": "<id>" } }`
Unbinds the node from the mesh group.

## `mode` (web)

**read** → `{ "operation": "read" }`

SDK model: `DeviceMode` (`get_device_mode()`). Sample response:
[`../api-responses/device_mode.json`](../api-responses/device_mode.json).

| Field | Meaning |
|-------|---------|
| `workmode` | `FAP` (gateway AP) / `HAP` / mobile variants (`Mobile_Router`, `Mobile_AP`, `LTE`, `Mobile_5G`). |
| `sysmode` | `Router` / `AP`. |
| `region.device` | Region code (`US`, …); read by the SDK as `region`. |

## `speedtest` & `get_server`

**speedtest** — `read` returns the current result, `write` starts a run, `stop`
aborts it.

**get_server** — `read` returns the speed-test server list; `clear` clears the
stored monthly history.

`speedinfo` (app) returns a compact snapshot: `support`, `up_speed`,
`down_speed`, `status` (`idle`, …), `last_speed_test_time`, `ping_time`,
`ping_jitter`.

## `timesetting`

**read / write** — node date/time/timezone. SDK model: `TimeSettings`
(`get_time_settings()`) with `time`, `date`, `timezone`, `tz_region`,
`continent`, `dst_status`. Write applies `date_time` / `timezone` /
`tz_region`. Full detail and the related `systime` / DST forms are in
[eco-mode-and-time.md](./eco-mode-and-time.md).

## `reboot` & `factory`

**reboot** → `{ "operation": "write", "params": { "device_id": "<id>" } }`
Reboots the named node, or the answering unit if it is the target; the master
can reboot the whole group.

The SDK's `deco.devices.reboot(*macs)` uses a second route, the one the community Home
Assistant integration (`amosyuen/ha-tplink-deco`) relies on:
`/admin/device?form=system` with
`{ "operation": "reboot", "params": { "mac_list": [ { "mac": "AA-BB-CC-DD-EE-FF" } ] } }`.
It takes node MACs, which `device_list` returns, whereas no read seen so far
returns a `device_id`. On a Deco X50-5G, `device_list` entries carry no
`device_id` field and a `read` on `form=system` answers `error_code=1`.

**factory** → `{ "operation": "write" }` Factory reset: erases `user-config`,
`device-config`, `group-info` (and `emmc-config` where supported), then reboots.

## `gateway`

**read** — reports gateway/master-role capability. Master transfer is handled
internally (`new_master_id` / `inherit_id` / `owner_transfer`) when a new master
is elected.

## `led` (app)

**read / write** — LED control. Read returns `leds.settings.enable` plus the
night-mode block (`night_mode`, `enable_night_mode`, `time_begin`, `time_end`).
Write toggles the LED and schedules auto-on/off (`auto_led`, `nightMode`).

## `eco_mode` (app)

**read / write** — power-saving mode (v1). Fields: `enable`, `user_set`,
`power_mode`/`type` (`normal_power` / `low_power` / `super_low_power`),
`schedule_enable`, `schedule_mode` (`custom` / `all_day`), `time_begin`,
`time_end`, `duration`, `eco_mode_duration`, `led_control_duration`,
`total_time`. The newer scheduler (v2) lives at
[`/admin/eco_mode`](./eco-mode-and-time.md).

---

## Notes

- `nickname` location presets: `bedroom`, `hallway`, `kitchen`, `living_room`,
  `master_bedroom`, `office`, `study`, `basement`, plus `custom`;
  `custom_nickname` is base64-encoded.
- `performance_limited` appears as an `exclude_feature` marker when the master
  syncs `device_list` from remote nodes.
- Node-targeted writes (`reboot`, `remove`, `device_prefer_set`) are relayed to
  the owning node through the internal `sync`/`connect` RPC when the target is
  not the answering unit.
- `mini_device_list` is a reduced node listing on the web UI; it is not exposed
  by the SDK.
