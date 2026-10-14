# Clients & reservations

Endpoints: **`/admin/client`** (served by both the web UI and the app) and
**`/admin/nrd`** (app). All forms use the
[encrypted envelope](../protocol/transport-and-dispatch.md).

`/admin/client` enumerates every device the mesh knows about, controls each
client's internet access / QoS priority, manages the MAC blacklist and the Wi-Fi
access-control lists, and owns the DHCP static reservations.

Related: [dhcp.md](./dhcp.md) (DHCP server / reservations),
[parental-control-and-qos.md](./parental-control-and-qos.md) (HomeShield
profiles & QoS), [homeshield-security.md](./homeshield-security.md).

---

## Forms

| Form | Operations | By | Purpose |
|------|-----------|-----|---------|
| `client_list` | read, write, remove | both | List, edit (name / type) and forget known clients. |
| `client` | — | both | Registered, but no `read` / `get` / `write` / `set` / `remove` callback answers on BE65 firmware 1.3.3. |
| `traffic_stat` | read (`list`) | both | Live per-client up/down speed & byte counters. |
| `client_access` | write | both | Toggle a single client's internet access (`mac` + `action`). |
| `black_list` | list, block, unblock | both | Mesh-wide internet blocklist. |
| `block` | write | both | Block a client (convenience write). |
| `unblock` | write | both | Unblock a client. |
| `addr_reservation` | getlist, add, modify, remove | both | DHCP static IP reservations (see [dhcp.md](./dhcp.md)). |
| `lease` | get | app | Current DHCP lease table. |
| `client_isolation` | read/write | app | Wi-Fi client-isolation toggle. |
| `access_refuse` | get | app | Wi-Fi access-control refused-client list. |
| `apply_list` | get, set | app | Wi-Fi access-control mode + apply list. |
| `white_list` | get | app | Wi-Fi access-control white list. |
| `/admin/nrd` · `black_list` | block, list, unblock | app | Network-Resource-Director (NRD) blacklist. |

> The endpoint rejects a reservation whose address collides with an existing
> lease or the LAN IP: `IP_CONFLICT`, `IP_CONFLICT_WITH_LAN_IP`,
> `IP_CONFLICT_WITH_RSVR_IP`.

---

## `client_list`

**read** → `{ "operation": "read" }`

Returns an array of client objects. Sample response:
[`../api-responses/client_list.json`](../api-responses/client_list.json).

| Field | Meaning |
|-------|---------|
| `mac` | Client MAC (colon-separated; SDK normalises). |
| `ip` | Current IPv4 address. |
| `name` | Display name — **base64-encoded** in the payload (SDK decodes). |
| `up_speed` / `down_speed` | Instantaneous upload / download rate (KB/s). |
| `wire_type` | `wired` or `wireless`. |
| `connection_type` | `wired`, `band2_4`, `band5`, `band6` (radio band). |
| `space_id` | HomeShield space / room id. |
| `access_host` | Id of the Deco node the client is connected through. |
| `interface` | Network the client sits on: `main`, `guest`, `iot`, `mlo`. |
| `client_type` | Device category: `iot_device`, `phone`, `pc`, `entertainment`, `other`, … |
| `owner_id` | HomeShield parental-control owner id (`""` if unassigned). |
| `remain_time` | Remaining allowed time in seconds (parental-control / priority window). |
| `online` | `true` if currently connected. |
| `client_mesh` | Reachable over the client-mesh / mesh backhaul. |
| `enable_priority` | QoS high-priority flag for this client. |

SDK model: `ClientDevice` (`ClientDevice.from_api`).

The raw payload carries extra fields not surfaced by the SDK model,
including `access_time`, `usr_set`, `name_usrset` / `type_usrset` (user-renamed
flags), `dcmp_cause`, `blocked`, `prio` / `prio_time` / `time_period`, and
`link_priority` (`band` / `device` auto-priority).

### `client_list` · write

Edits clients in place. Verified on a BE65 (firmware 1.3.3):

```json
{ "operation": "write",
  "params": { "client_list": [
    { "mac": "6A-7A-D6-9B-16-7F", "name": "<base64>",
      "user_set_name_type": true, "client_type": "pc" } ] } }
```

The firmware **silently ignores** an entry unless it carries `name` together
with `user_set_name_type: true`; when it does, `client_type` is applied in the
same write. A write with only `mac` + `client_type` (with or without
`has_set_client_type` / `custom_client_type`) is acknowledged but changes
nothing. SDK: `DecoClient.clients.update()`.

### `client_list` · remove

Forgets offline clients; a device that reconnects is listed again.

```json
{ "operation": "remove", "params": { "client_list": [ { "mac": "14-35-B7-74-06-5C" } ] } }
```

SDK: `DecoClient.clients.remove()`.

## `client`

Per-client settings in the web UI (name, type, QoS priority, owner). On BE65
firmware 1.3.3 every probed operation (`read`, `get`, `write`, `set`,
`remove`) answers `error_code: 1` / `"no such callback"`; use
[`client_list` · write](#client_list--write) instead.

Setting priority is capped: exceeding the maximum returns *"Unable to set client
priority. Maximum client number exceeded."* On QoS hardware a write toggles the
device's QoS class, and requires that a bandwidth ceiling has been set (see
[`bandwidth`](./parental-control-and-qos.md)).

## `traffic_stat`

**read** (`list`) — live per-client statistics: `up_speed`, `down_speed`, and
cumulative `retx_byte` / `rerx_byte`, keyed by `mac`.

## `client_access`

**write** → `{ "operation": "write", "params": { "mac": "<MAC>", "action": … } }`

Allow / refuse a single client's internet access. Present in both the web and
app forms.

## `black_list` / `block` / `unblock`

- `black_list` — verified operations are **list**, **block** and **unblock**
  (`getlist` and `add` answer `"no such callback"`). Each entry stores `mac`,
  `name` (base64) and `client_type`. Adding is capped (*"Unable to add. Maximum
  number exceeded"*) and also drives the NRD block.

  ```json
  { "operation": "list" }
  { "operation": "block",
    "params": { "client_list": [ { "mac": "02-00-00-00-00-01", "name": "<base64>", "client_type": "other" } ] } }
  { "operation": "unblock", "params": { "client_list": [ "02-00-00-00-00-01" ] } }
  ```

  `list` returns `{ "client_list": [ … ] }`, or `{ "client_list": {} }` when
  the blocklist is empty. `block` / `unblock` acknowledge with an unencrypted
  `{ "error_code": 0 }`. SDK: `DecoClient.clients.get_blocked()` / `block()` /
  `unblock()`.
- `block` / `unblock` — **write** convenience forms that block / unblock a
  client without editing the blacklist collection directly.

## `addr_reservation`

**getlist / add / modify / remove** — DHCP static IP reservations (MAC → IP).
A per-table maximum bounds the number of reservations. Verified on a BE65 (firmware 1.3.3):

```json
{ "operation": "getlist" }
{ "operation": "add",
  "params": { "reservation_list": [ { "mac": "02-00-00-00-00-01", "ip": "192.168.5.250" } ] } }
{ "operation": "modify",
  "params": { "mac": "02-00-00-00-00-01", "ip": "192.168.5.251",
              "original_mac": "02-00-00-00-00-01", "original_ip": "192.168.5.250" } }
{ "operation": "remove", "params": { "reservation_list": [ "02-00-00-00-00-01" ] } }
```

`getlist` returns `{ "reservation_list": [ { "mac", "ip" } ],
"reservation_list_max_count": 200 }`; `remove` acknowledges with an unencrypted
`{ "error_code": 0 }`. SDK: `DecoClient.address_reservations`. A new or modified
reservation is validated against the LAN subnet and rejected with `IP_CONFLICT`
/ `IP_CONFLICT_WITH_LAN_IP` / `IP_CONFLICT_WITH_RSVR_IP`. See
[dhcp.md](./dhcp.md) for the DHCP server itself.

## Access control (app)

App-only Wi-Fi access-control forms:

| Form | Op | Detail |
|------|-----|--------|
| `client_isolation` | read/write | Isolate wireless clients from each other. |
| `access_refuse` | get | Refused-client list gathered from the radios. |
| `apply_list` | get, set | Access-control `curr_mode` (`white` / `block`), `guest_network_access`, `new_device_notify`, and the applied client list. |
| `white_list` | get | The Wi-Fi access-control white list. |
| `lease` | get | Current DHCP leases. |

> `white_list` here is the **Wi-Fi access-control** allow-list. HomeShield's
> content-filter whitelist is a different `white_list` form under
> [`/admin/smart_network`](./parental-control-and-qos.md).

## `/admin/nrd` · `black_list`

**block / list / unblock** — the Network-Resource-Director blacklist. A parallel
MAC blacklist to `/admin/client`'s, used by the NRD subsystem; entries carry
`mac`, `name`, `client_type`.

---

## Notes

- `client_access`, `client_list`, `client`, `traffic_stat`, `black_list`,
  `block`, `unblock` and `addr_reservation` are served by **both** the web UI
  and the app at `/admin/client` (see
  [merge behaviour](../protocol/transport-and-dispatch.md#controller-merge-behaviour)).
  `lease`, `client_isolation`, `access_refuse`, `apply_list` and `white_list`
  are app-only.
- `name` is base64-encoded on the wire — decode before display and encode on
  write.
- `owner_id` links a client to a HomeShield parental-control profile managed via
  [`/admin/smart_network` · `patrol_owner` / `patrol_cli`](./parental-control-and-qos.md).
- The app can mirror access / blacklist changes to the TP-Link cloud when
  smart-home support is enabled.
