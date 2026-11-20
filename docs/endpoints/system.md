# System — language, logout, components & locale

Endpoints: **`/admin/system`**, **`/admin/component_control`**, **`/admin/web`**
and the top-level **`/locale`** (all web). Auth is the
[encrypted envelope](../protocol/transport-and-dispatch.md) except where marked
**plain** (`envar` and `sysmode` are on the
[plaintext list](../protocol/transport-and-dispatch.md#plaintext-endpoints)).

Related: [login.md](./login.md) (`logout` ends the session),
[device.md](./device.md) (per-node `envar` / `sysmode`),
[network.md](./network.md) (`erp_setting` / `fast_xmit_setting` toggled by
`extra_component_info`), [README.md](./README.md).

---

## Forms

| Endpoint | Form | Operations | By | Purpose |
|----------|------|-----------|-----|---------|
| `/admin/system` | `envar` | read, write | web | Environment variables (UI language). **plain** |
| `/admin/system` | `sysmode` | read | web | System mode. **plain** |
| `/admin/system` | `logout` | write | web | Drop the current session. |
| `/admin/component_control` | `switch_list` | read | web | Feature/component on-off list. |
| `/admin/web` | `extra_component_info` | get | web | Extra component/capability info. |
| `/locale` | `lang` | read, write | web | UI locale (`en_US`, …). |
| `/locale` | `country` | read/write | web | Device country. |
| `/locale` | `country_list` | read | web | Supported country list. |

---

## `/admin/system?form=envar`

**read / write** · **Auth:** plaintext

Environment variables. Reads and writes the UI language `ui_language`,
defaulting the locale to `EN_US`. Write sets the active UI language.

```json
{ "operation": "write", "params": { "ui_language": "EN_US" } }
```

Supported `ui_language` values (code → name):

`BG_BG` Bulgarian · `CS_CZ` Czech · `DA_DK` Danish · `DE_DE` German ·
`EN_US` American · `ES_ES` Spanish · `FI_FI` Finnish · `FR_FR` French ·
`IT_IT` Italian · `JP_JP` Japanese · `KO_KR` Korean · `NL_NL` Dutch ·
`NO_NO` Norwegian · `PL_PL` Polish · `PT_PT` Portuguese · `RO_RO` Romanian ·
`RU_RU` Russian · `SK_SK` Slovak · `SV_SE` Swedish · `TH_TH` Thai ·
`TR_TR` Turkish · `UK_UA` Ukrainian · `VI_VN` Vietnamese ·
`ZH_TW` Traditional Chinese.

## `/admin/system?form=sysmode`

**read** · **Auth:** plaintext

Reports the system mode. On a Deco X50-5G (firmware 1.1.3) this form
answers `{}` through the encrypted envelope and HTTP 403 in plaintext; use
[`/admin/device?form=mode`](./device.md) (SDK `get_device_mode().sysmode`,
e.g. `Mobile_5G`) instead. `sysmode` is also served per node by the app device
endpoint ([`/admin/device?form=sysmode`](./device.md)) — treat availability as
model-dependent.

## `/admin/system?form=logout`

**write** — invalidates the session. The SDK also discards its `stok`
client-side. See [login.md](./login.md#session-lifecycle).

## `/admin/component_control?form=switch_list`

**read** — returns the list of feature/component on-off switches, including
`show_performance` (whether the web UI shows the CPU/memory
[`performance`](./network.md) panel); additional component flags are returned in
the same list.

## `/admin/web?form=extra_component_info`

**get** — extra component/capability info. Derived from model support:
`enable_erp` (`is_erp_support`), `enable_erp_standby` (`is_standby_support`)
and `enable_fast_xmit`. These gate the network-side `erp_setting` /
`fast_xmit_setting` forms in [network.md](./network.md).

## `/locale?form=lang`

**read / write** — UI locale.

- **read** returns the current `locale` (default `en_US`), the `model` and
  `rebootTime`; falls back to the browser `HTTP_ACCEPT_LANGUAGE` when unset.
- **write** sets `locale` (validated as word characters / underscore); rejected
  with `locale change is forbidden` when locale changes are locked, or
  `invalid args` on a malformed value.

## `/locale?form=country` & `country_list`

**country** — read / write the device country, returning `value` / `name`.

**country_list** — read the supported countries. Names seen:
`UNITED_KINGDOM`, `RUSSIA`, `KOREA_REPUBLIC`, `POLAND`, `TAIWAN`, `VIETNAM`,
`ROMANIA`, `UNITED_STATES`, `BRAZIL`, `JAPAN`, `CANADA`, `SAUDI_ARABIA`,
`INDONESIA`.

---

## Notes

- The same `BG_BG…ZH_TW` language table is available through both
  `/admin/system?form=envar` and the node
  [`/admin/device?form=envar`](./device.md), so `ui_language` can be
  read/written through either.
- `/locale` is a top-level endpoint (not under `/admin`).
