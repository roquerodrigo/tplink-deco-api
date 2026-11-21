# Network — WAN / LAN / IPv6 / VLAN

Endpoint: **`/admin/network`**. Served by both the web UI and the app; app-only
forms are marked in the By column. All forms use the
[encrypted envelope](../protocol/transport-and-dispatch.md).

Most reads accept `"params": { "device_mac": "default" }` to target the
gateway or a specific mesh node.

Related: [routing.md](./routing.md) (static routes),
[dhcp.md](./dhcp.md) (DHCP server), [system.md](./system.md).

---

## Forms

| Form | Operations | By | Purpose |
|------|-----------|-----|---------|
| `wan_mode` | read/write | web | WAN operating mode (router / bridge / passthrough). |
| `wan_ipv4` | read, write, connect, disconnect | both | IPv4 WAN config & dial control. |
| `lan_ipv4` | read | both | Read-only LAN IPv4 snapshot. |
| `lan_ip` | read/write | both | LAN IP + subnet mask. |
| `lan_block` | read/write | app | Subnet-block / expanded-subnet control. |
| `internet` | read | both | Aggregate internet reachability. |
| `ipv6` | read/write | both | IPv6 WAN/LAN configuration. |
| `vlan` | read/write | both | WAN VLAN tagging. |
| `mac_clone` | read/write | both | WAN MAC address clone. |
| `mac_clone_list` | read | app | Candidate MACs to clone. |
| `performance` | read | both | Gateway CPU / memory usage. |
| `dhcp_dial` | read/write | both | DHCP-mode WAN dial settings. |
| `igmp_setting` | read/write | web | IGMP snooping / proxy. |
| `wifi_network` | read/write | web | Wi-Fi ↔ network binding. |
| `erp_setting` | read/write | web | Energy-related platform settings. |
| `fast_xmit_setting` | read/write | web | Fast-transmit tuning. |
| `upnp` | read/write | app | UPnP IGD enable + port list. |
| `routes_static` | getlist, add, modify, remove | app | Static routes (see [routing.md](./routing.md)). |
| `routes_system` | getlist | app | System (auto) routes. |
| `dsl_status` | read | both | DSL physical-layer status (DSL models only). |

> `dsl_status` is available on DSL-capable hardware only.

---

## `wan_ipv4`

**read** → `{ "operation": "read", "params": { "device_mac": "default" } }`

Result (`result.wan` / `result.lan`):

| Field | Where | Meaning |
|-------|-------|---------|
| `wan.dial_type` | WAN | `dynamic_ip`, `static_ip`, `pppoe`, `l2tp`, `pptp`, `dslite`, `v6_plus`, `lte`, `ocn`, `mobile_bridge`, `pppoa`. |
| `wan.enable_auto_dns` | WAN | Whether DNS is obtained automatically. |
| `wan.ip_info.{ip,mask,mac,gateway,dns1,dns2}` | WAN | Active IPv4 addressing. |
| `wan.ip1_info` | WAN | Secondary block for `l2tp`/`pptp` (tunnel local IP). |
| `wan.mobile_cpe` | WAN | Cellular fields for `lte` (`rsrp`, `rsrq`, `snr`, `rssi`, `sim_status`, `network_type`, `data_usage`, …). |
| `lan.ip_info.{ip,mask,mac,gateway,dns1,dns2}` | LAN | LAN addressing. |

The SDK models this as `WanInfo` (`get_wan_info(device_mac="default")`).
With `dial_type: "lte"` the router sends the addressing in `wan.mobile_cpe`
(`ip`, `mask`, `gateway`, `dns1`, `dns2`, `mac`) and no `ip_info`; the SDK
reads `WanDetails.ip_info` from `mobile_cpe` in that case.

**write** — set the WAN protocol and its parameters. `params` carries
`wan_type`/`dial_type` plus proto-specific fields (static IP block, PPPoE
credentials, VLAN, etc.). `dial_type` is validated against the list above.

**connect / disconnect** — bring the WAN dial up or down without changing the
stored configuration.

## `internet`

**read** → `{ "operation": "read" }`

Result:

| Field | Meaning |
|-------|---------|
| `ipv4.inet_status` | `online` / `offline`. |
| `ipv4.dial_status` | Dial state (`connected`, `disconnected`, …). |
| `ipv4.connect_type` | Detected connection type. |
| `ipv4.auto_detect_type` | Auto-detected WAN type. |
| `ipv4.error_code` | Per-stack error. |
| `ipv6.*` | Same shape for IPv6. |
| `link_status` | Physical WAN link (`up`/`down`). |
| `mobile_cpe` | Present on LTE/5G modes instead of `ipv4`. |

`mobile_cpe` fields seen on a Deco X50-5G (firmware 1.1.3): `inet_status`,
`dial_status`, `sim_status` (`ready`, …), `network_type` (`nr`, …),
`signal_strength`, `rsrp`, `rsrq`, `snr`, `rssi`, `uplink_rate`,
`downlink_rate`, `data_usage`, `limit_mode`, `profile_name` (base64) and
`sim_number`. That model sends no `ipv4`, `ipv6` or `link_status` block.

SDK model: `InternetStatus` (`get_internet_status()`). On LTE/5G models
`InternetStatus.mobile` holds a `MobileStatus` (with `profile_name` decoded)
and `ipv4.inet_status` / `ipv4.dial_status` are copied from it.

## `lan_ip`

**read / write** → `params: { "device_mac": "default" }`

| Field | Meaning |
|-------|---------|
| `mac_addr` | Node MAC. |
| `lan_ip.ip` | LAN IPv4 address. |
| `lan_ip.mask` | Subnet mask / mask type. |
| `dns_server_ip` | DNS servers the node hands out (list). |
| `wan_ip` | Current WAN IPv4 addresses (list). |

The read needs `params.device_mac`; without it the X50-5G answers HTTP 500.
SDK: `deco.network.get_lan_ip(device_mac="default")` → `LanIp`, and
`deco.network.set_lan_ip(ip, mask, device_mac="default")`, which sends
`{ "operation": "write", "params": { "device_mac": …, "lan_ip": { "ip": …, "mask": … } } }`.
The write payload mirrors the read shape and has not been checked on
hardware.

## `vlan`

**read / write** — WAN VLAN tagging for ISP setups. `params` carries `vlan_id`
and status; a `vlan_id` already used by IPTV is rejected.

## `mac_clone`

**read / write** — clone a chosen MAC onto the WAN interface. Write `params`:
`{ "clone_mode": "custom"|"default", "mac": "…" }`. `mac_clone_list` (app)
enumerates candidate MACs.

## `performance`

**read** → `{ "operation": "read" }`

```json
{ "result": { "cpu_usage": 0.05, "mem_usage": 0.42 }, "error_code": 0 }
```

Both values are normalised to `[0.0, 1.0]`. SDK model: `Performance`
(`get_performance()`). Example:
[`../api-responses/performance.json`](../api-responses/performance.json).

## `dsl_status`

**read** → `params: { "device_mac": "default" }`. Only meaningful on DSL
hardware; non-DSL models return an empty result (all zeros) or reject the form.

Result (`dsl_cfg`): `status`, `dsl_up_time`, `modulation_type`, `annex`,
`upstream_curr_rate` / `downstream_curr_rate`, `upstream_max_rate` /
`downstream_max_rate`, `upstream_noise_margin` / `downstream_noise_margin`,
`upstream_attenuation` / `downstream_attenuation`, `ATUCCRCErrors`, `CRCErrors`.
SDK model: `DslStatus` (`get_dsl_status()`).

## `ipv6`

**read / write** — IPv6 WAN mode (`dynamic_ipv6`, `dhcpv6`, `pppoev6`,
`v6_plus`, `dslite`, `bridge`, `passthrough`) plus prefix/DNS. Field set mirrors
`wan_ipv4` with IPv6 addressing.

## `upnp` (app)

**read / write** — enable UPnP IGD and read the active port-mapping list
(`is_enabled`, `description`, `external_port`, `internal_port`, `client_ip`,
`protocol`, `leasetime`).

## `lan_block` (app)

**read / write** — LAN subnet sizing (block / expand the subnet range).

---

## Notes

- `wan.dial_type` drives which sub-object holds the addressing (`ip_info`,
  `ip1_info`, or `mobile_cpe`).
- On LTE/5G gateways, `internet` and `wan_ipv4` return `mobile_cpe` (signal,
  SIM, data-usage) instead of the IPv4 block.
- `dhcp_dial` here is the WAN-side DHCP dial; the LAN DHCP *server* lives at
  [`/admin/dhcp`](./dhcp.md).
</content>
