# Endpoint index

Complete map of every local endpoint exposed by the firmware, grouped by
functionality. Each row is `controller → form → operations`. All paths are
relative to:

```
https://<router-ip>/cgi-bin/luci/;stok=<TOKEN>/…
```

Legend:

- **Auth** — `enc` = AES/RSA envelope (default), `plain` = plaintext JSON.
- **By** — which client the form serves: `web` (web UI), `app` (mobile app),
  or `both` (the dispatcher merges the two form sets at one URL).
- Operation names are the JSON `operation` values. `read`/`write` and
  `get`/`set` are used interchangeably by different endpoints.

See [`../protocol/transport-and-dispatch.md`](../protocol/transport-and-dispatch.md)
for the request/response contract and
[`../auth-protocol.md`](../auth-protocol.md) for the crypto envelope.

---

## Login & session — [login.md](./login.md)

| Endpoint | Form | Operations | Auth |
|----------|------|-----------|------|
| `/login` | `auth` | read | plain |
| `/login` | `keys` | read | plain |
| `/login` | `login` | login | enc |
| `/login` | `check_factory_default` | read | plain |
| `/login` | `default_info` | read | plain |
| `/login` | `mini_login`, `cloud_login` | login | enc |
| `/domain_login` | `dlogin` | read/write | enc |

## Network: WAN / LAN / IPv6 / VLAN — [network.md](./network.md)

Served at `/admin/network` (web + app merged).

| Form | Operations | By |
|------|-----------|-----|
| `wan_mode` | read/write | web |
| `wan_ipv4` | read, write, connect, disconnect | both |
| `lan_ipv4` | read | both |
| `lan_ip` | read/write | both |
| `lan_block` | read/write | app |
| `internet` | read | both |
| `ipv6` | read/write | both |
| `vlan` | read/write (`get_vlan`/`set_vlan`) | both |
| `mac_clone` | read/write | both |
| `mac_clone_list` | read | app |
| `performance` | read | both |
| `dhcp_dial` | read/write | both |
| `igmp_setting` | read/write | web |
| `wifi_network` | read/write | web |
| `erp_setting` | read/write | web |
| `fast_xmit_setting` | read/write | web |
| `upnp` | read/write | app |
| `routes_static` | getlist, add, modify, remove | app |
| `routes_system` | getlist | app |

## Static routing — [routing.md](./routing.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/route` | (route table: `wan`/`lan`/`internet` interfaces) | insert, delete, update, read |
| `/admin/network` | `routes_static`, `routes_system` | see network.md |

## DHCP server — [dhcp.md](./dhcp.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/dhcp` | `dhcp_info` | read, write |
| `/admin/dhcp` | `dhcp_dial` | set |
| `/admin/dhcp` | `dhcp_ap` | get, set |

## Wi-Fi — [wireless.md](./wireless.md)

Served at `/admin/wireless` (web + app merged).

| Form | Operations | By |
|------|-----------|-----|
| `wlan` | read, write | both |
| `operation_mode` | read/write | both |
| `bridge` | read (`get_bridge_status`) | both |
| `check` | check | both |
| `ieee80211r` | read/write | both |
| `beamforming` | read/write | both |
| `bandwidth_enhance` | read/write | both |
| `bandwidth_switch` | read/write | app |
| `power` | read/write | both |
| `smart_antenna` | read/write | app |
| `wifi_schedule` | read/write | app |
| `ofdma` | read/write | app |
| `mlo_network` | read/write | app |
| `backhaul_optimization` | read/write | app |
| `get_support` | read | app |
| `/admin/network_optimize` · `acs_optimize` | read, write | app |
| `/admin/network_optimize` · `acs_filter_macs` | get | app |

## Deco nodes & speed test — [device.md](./device.md)

Served at `/admin/device` (web + app merged).

| Form | Operations | By |
|------|-----------|-----|
| `device_list` | read, remove | both |
| `mode` | read | web |
| `speedtest` | read, write, stop | both |
| `speedinfo` | read | app |
| `timesetting` | read, write | both |
| `system` | read, write | both |
| `reboot` | write | both |
| `factory` | write | both |
| `gateway` | read | both |
| `get_server` | read, clear | both |
| `led` | read/write | app |
| `sysmode` | read | app |
| `set_backup` | write | app |
| `device_prefer_set` | set | app |
| `signal_level_list` | read | app |
| `detect_mode` | read | app |
| `fixed_wan_port` | read/write | app |
| `systime` | read | app |
| `eco_mode` | read/write | app |

## System — [system.md](./system.md)

| Endpoint | Form | Operations | Auth |
|----------|------|-----------|------|
| `/admin/system` | `envar` | read, write | plain |
| `/admin/system` | `sysmode` | read | plain |
| `/admin/system` | `logout` | write | enc |
| `/admin/component_control` | `switch_list` | read | enc |
| `/admin/web` | `extra_component_info` | get | enc |
| `/locale` | `lang` | read, write | enc |
| `/locale` | `country`, `country_list` | read | enc |

## Eco mode & time — [eco-mode-and-time.md](./eco-mode-and-time.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/eco_mode` | `eco_mode` | read, write |
| `/admin/eco_mode` | `get_period` | read |
| `/admin/eco_mode` | `skip_schedule` | write |
| `/admin/time_setting` | `request`, `notify` | (DST/time sync) |
| `/admin/device` | `timesetting`, `systime` | read, write |

## Clients & reservations — [clients.md](./clients.md)

Served at `/admin/client` (web + app merged).

| Form | Operations | By |
|------|-----------|-----|
| `client_list` | read, write, remove | both |
| `client` | — (no callback answers `read`, `get`, `write`, `set` or `remove`) | both |
| `traffic_stat` | read | both |
| `black_list` | list, block, unblock | both |
| `block` / `unblock` | write | both |
| `addr_reservation` | getlist, add, modify, remove | both |
| `client_access` | write | both |
| `client_isolation` | read/write | app |
| `access_refuse` | write | app |
| `apply_list` | get, set | app |
| `white_list` | get | app |
| `lease` | get | app |
| `/admin/nrd` · `black_list` | block, list, unblock | app |

## Parental controls & QoS — [parental-control-and-qos.md](./parental-control-and-qos.md)

Served at `/admin/smart_network`.

| Form | Operations |
|------|-----------|
| `tm_qos` | read, write |
| `bandwidth` | get, set |
| `patrol_owner` | list, add, del, block, get, set |
| `patrol_insights` | get, remove, history |
| `patrol_cli` | add, del |
| `patrol_filter` | (website filter add/del/list) |
| `patrol_owner_avatar` | get, set |
| `white_list` | get, add, remove |
| `app_block_list` | read |
| `app_dpi` | add, modify, remove |
| `time_limit_add` / `time_limit_modify` / `time_limit_remove` | write |
| `tmp_avira` | (HomeShield/Avira parental-control bridge) |

## HomeShield security — [homeshield-security.md](./homeshield-security.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/security` | `info` | read, write |
| `/admin/security` | `category`, `rule` | read |
| `/admin/security` | `history` | get, clear, remove |
| `/admin/security` | `update` | write |
| `/admin/camera_security` | `camera_security` | get, set |
| `/admin/camera_security` | `camera_security_blocked_period` | get, set |

## Firmware & upgrade — [firmware-and-upgrade.md](./firmware-and-upgrade.md)

| Endpoint | Form | Operations | Auth |
|----------|------|-----------|------|
| `/admin/firmware` | `config` | read, check, backup, restore | enc |
| `/admin/firmware` | `config_multipart` | (upload) | plain |
| `/admin/firmware` | `upgrade` | write | enc |
| `/mcu_upgrade` | `mcu_upgrade` | check | enc |
| `/admin/cloud` | `firmware` | check, upgrade, download, status | mixed |
| `/admin/sync` | firmware sync/download | see cloud-and-account.md | enc |

## Cloud & account — [cloud-and-account.md](./cloud-and-account.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/cloud` | `nickname` | read, write |
| `/admin/cloud` | `firmware` | check, upgrade, download, status |
| `/admin/cloud` | `group` | create, add, get, set, update, remove, report, message, push |
| `/admin/cloud` | `system` | bind, unbind, remove_all, proxy, account, notify |
| `/admin/cloud` | `ddns`, `manager`, `iot_read` | — |
| `/admin/cloud_account` | `read` | read_keys, get_device_token, get_deviceInfo |
| `/admin/cloud_account` | `login` | user_login, bind_and_login |
| `/admin/cloud_account` | `check_internet`/`check_device`/`check_connection`/`check_login` | read |
| `/admin/cloud_account` | `bind_owner`/`unbind_owner` | write |
| `/admin/cloud_account` | `get_dev_info`/`set_dev_info` | read/write |
| `/admin/cloud_account` | `cloud_pass_through` | write |
| `/admin/cloud_account` | `upgrade`, `get_token`, `tmp_cmd` | — |

## IoT & smart home — [iot-smart-home.md](./iot-smart-home.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/iot_device` | `iotdevice` | getlist, add, modify, remove, scan, begin_scan, end_scan, identify, getlist_by_mod, account_sync, `inner_*` |
| `/admin/iot_device` | `iotprofile` | get_and_update_pwd |
| `/admin/iot_device` | `iotspace` | set, set_network_device, remove_network_device |
| `/admin/iot_device` | `iotowner`, `iotrole` | get/set, get_init_info, commission_complete, get_pairing_code |
| `/admin/iot_automation` | `iotautomation` | get_tasklist, add_task, modify_task, remove_tasklist, add_trigger, modify_trigger, remove_triggerlist |
| `/admin/iot_automation` | `iotoneclick` | getlist, set, add_scene, modify_scene, remove_scene, add_action, modify_action, remove_actionlist, get_history, remove_history |
| `/admin/iot_cloud` | `iot_cloud_req` | index (alexa / ifttt) |
| `/admin/iot_client_mesh` | `client_mesh` | set, tss, sync_device_msg, sync_cloud_msg |
| `/admin/msg_server` | `coordinator`, `notify` | — |

## WPS — [wps.md](./wps.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/wps` | `status` | get |
| `/admin/wps` | `state` | set |
| `/admin/wpsd` | `main`, `code` | report (internal) |

## VPN — [vpn.md](./vpn.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/vpn_client` | `config` | read, write, load, insert, update, remove |
| `/admin/vpn_server` | `server` | read, insert, remove, update |
| `/admin/vpn_server` | `accounts` | insert, remove, update |
| `/admin/vpn_server` | `cert` | set, get |
| `/admin/vpn_server` | `key` | renews, renewc, gets, getc |
| `/admin/vpnconn` | `conn` | list, disconnect |
| `/admin/vpnconn` | `cert`, `sync` | — |

## NAT & port forwarding — [nat-port-forwarding.md](./nat-port-forwarding.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/nat` | `setting` | read, write |
| `/admin/nat` | `vs` | getlist, add, modify, batch_remove, remove |
| `/admin/nat` | `pt` | load, insert, update |
| `/admin/nat` | `dmz` | read, write |
| `/admin/nat` | `alg` | get, write |
| `/admin/nat` | `sip_alg` | get, set |

## Dynamic DNS — [ddns.md](./ddns.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/ddns` | `ddns` | get, set |

## IPv6 firewall — [ipv6-firewall.md](./ipv6-firewall.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/ipv6_firewall` | `firewall` | read, write, remove, modify |
| `/admin/ipv6_firewall` | `client` | read |

## IPTV — [iptv.md](./iptv.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/iptv` | `iptv` | get, set |

## USB storage & Time Machine — [storage-usb.md](./storage-usb.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/usbshare` | `device` | scan, list, remove, list_all, remove_list |
| `/admin/usbshare` | `server` | read, write, read_list, write_list |
| `/admin/usbshare` | `status`, `sync` | read |
| `/admin/time_machine` | `settings` | read, write |
| `/admin/time_machine` | `info`, `content` | read |

## Administration & remote management — [administration.md](./administration.md)

Served at `/admin/administration`.

| Form | Operations |
|------|-----------|
| `account` | read, write, set, appset, appget, mcu_read, mcu_write, mcu_check |
| `recovery` | read, update |
| `mode` | local, remote |
| `local` | load, insert, update, remove, view |
| `remote` | read, write |
| `login` | read, write |

## Onboarding & provisioning — [onboarding-and-provisioning.md](./onboarding-and-provisioning.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/quick_setup` | `newgroup`, `newdevice`, `batchdevices` | write |
| `/admin/quick_setup` | `preconf` | read, write, add |
| `/admin/quick_setup` | `heartbeat`, `sync`, `eponymous_detect`, `bluetooth`, `tss`, `get_dev_list` | — |
| `/admin/tipc-controller` | `newdevice`, `sync` | write |
| `/discover` | `_discover` | read |
| `/discover` | `sync_config`, `sync_slave_check`, `sync_master_check` | — |
| `/admin/sync` | mesh config/firmware sync | (internal) |

## Logs & diagnostics — [logs-and-diagnostics.md](./logs-and-diagnostics.md)

| Endpoint | Form | Operations | Auth |
|----------|------|-----------|------|
| `/admin/log` | `log` | read, write, load | enc |
| `/admin/log_export` | `types` | read | enc |
| `/admin/log_export` | `save` | write | enc |
| `/admin/log_export` | `save_log` | (download) | plain |
| `/admin/log_export` | `feedback_log` | build | enc |
| `/admin/telemetry_collect` | `telemetry_device`/`_client`/`_system`/`_usb` | read | enc |
| `/admin/telemetry_collect` | `telemetry_control` | write | enc |
| `/admin/debug` | `qlog`/`simplecom`/`tty2tcp`/`tm` | start, stop | enc |
| `/admin/auto_test` | `test` | nat, upnp, dhcp, wifi, all_info | enc |
| `/admin/arptbl` | `syn` | tbl_op | enc |

## Other services — [misc-services.md](./misc-services.md)

| Endpoint | Form | Operations |
|----------|------|-----------|
| `/admin/cwmp` | `cwmp` | get, set |
| `/admin/combo_port` | `list` | read |
| `/admin/combo_port` | `switch` | set |
| `/admin/component_list` | `mobile` | read |
| `/admin/component_list` | `bluetooth`, `profile` | read |
| `/admin/ga_info` | `status` | read, write, get, get_internal |
| `/admin/op_manager` | `read` | get, list, getlist (opcode/subconfig proxy) |
| `/blocking` | `check` | get, set |
| `/blocking` | `vercode` | read, write |
| `/admin/wifidog` | `portal_content` | read, upload |
| `/admin/conn-indicator` | `internet` | down, sync |
| `/admin/re_disconnect_cloud` | `notify` | write |

---

## Coverage

Every request path the router serves is represented above (67 controllers,
web + app). The `/admin` root itself is an access-control guard, not an API
endpoint, and is intentionally omitted.
</content>
