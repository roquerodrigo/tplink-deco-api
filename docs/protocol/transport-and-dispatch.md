# Transport & request dispatch

How every local request is addressed, dispatched, wrapped and answered. For
the cryptographic envelope and the login handshake see
[`../auth-protocol.md`](../auth-protocol.md); this page covers the layer around
it — URLs, the `form`/`operation`/`params` contract, the response envelope,
error codes and batching.

---

## URL layout

```
https://<router-ip>/cgi-bin/luci/;stok=<TOKEN>/<controller>?form=<form>
```

| Part | Meaning |
|------|---------|
| `cgi-bin/luci` | The router's CGI entry point. |
| `;stok=<TOKEN>` | Session token, injected as a path parameter. Empty (`;stok=/`) before login, populated afterward. |
| `<controller>` | Request path segment: `login`, `admin/network`, `admin/wireless`, … |
| `?form=<form>` | Selects a handler group inside the controller. |

The base string is `"/cgi-bin/luci/;stok=" + stok + path`. A second, rarely
used entry point exists — `/cgi-bin/ozker/;stok=` — for a parallel CGI backend;
the Deco API proper uses the `cgi-bin/luci` one.

- **Transport:** HTTPS on modern firmware (self-signed); older units accept
  plain HTTP. The SDK defaults to `https://`.
- **Method:** always `POST`. The query string carries only `form`.
- **`Content-Type: application/json`** for every call.

---

## Request body

### Encrypted requests (default)

```json
{
  "sign": "<hex RSA signature>",
  "data": "<base64 AES-CBC-PKCS7 ciphertext>"
}
```

`data` decrypts to the *logical* request:

```json
{ "operation": "<operation>", "params": { … } }
```

The envelope (AES key derivation, `sign` string, `seq` counter, block
splitting) is fully specified in [`../auth-protocol.md`](../auth-protocol.md).

### Plaintext requests

A fixed set of endpoints skip the envelope and take the logical request
directly as the JSON body. See [Plaintext endpoints](#plaintext-endpoints).

### The `operation` verb

`operation` selects a callback inside the form's handler group. The vocabulary
is small and consistent across controllers:

| Operation | Meaning |
|-----------|---------|
| `read` / `get` | Fetch current state. |
| `write` / `set` | Replace / apply state. |
| `load` | Fetch supporting data for a form (ranges, options, capabilities). |
| `add` / `insert` | Create a new entry in a list. |
| `modify` / `update` | Change an existing list entry. |
| `remove` / `delete` | Delete a list entry. |
| `getlist` / `list` | Enumerate a collection. |
| form-specific verbs | Some forms define custom verbs (`connect`, `disconnect`, `block`, `unblock`, `upgrade`, `reboot`, `factory`, `login`, …). |

Whether a form is addressed with `read`/`write` or `get`/`set` depends on the
form; the per-endpoint pages list what each accepts.

### The `params` object

Form-specific input. Many read operations target a specific node with:

```json
{ "operation": "read", "params": { "device_mac": "default" } }
```

`"default"` means the gateway / the node answering the request. A real MAC
(colon or dash separated depending on the form) targets one mesh node.

---

## Response envelope

The dispatcher answers with a uniform JSON object:

```json
{
  "error_code": 0,
  "result": { … }
}
```

| Key | Notes |
|-----|-------|
| `error_code` | `0` on success, non-zero on failure. Present on every response. |
| `result` | Payload on success. Object or array depending on the form. Some forms use `data` instead of `result`. |
| `msg` | Human-readable error text on failure. |
| `config_version` | Echoed configuration version on writes that mutate persisted config. |

On an **encrypted** call the whole object above is itself AES-encrypted and
base64-encoded in the HTTP body (same envelope as the request `data`), then
decrypted client-side. Plaintext calls return the object directly.

### Success vs. error

```json
{ "error_code": 0, "result": { "stok": "…", "usr_lvl": 1 } }
```

```json
{ "error_code": -40401, "msg": "invalid args" }
```

`error_code` is the single source of truth — a `200 OK` with a non-zero
`error_code` is still an application error. The SDK raises `ApiError` in that
case.

### Known error codes

Error codes are negative integers. Values seen in practice include
authentication failures (`-40401` family), "invalid args", "maximum number
exceeded", per-feature codes (e.g. HomeShield uses `-3401`, `-3403`, `-3404`,
`-4101…-4105`, `-6101`, `-6102`) and generic "Unknown error". They are
feature-specific; treat any non-zero value as failure and surface `msg`.

---

## Batch requests

The dispatcher supports combining several form calls into one HTTP round-trip:
the request carries prefixed sub-calls and the response un-prefixes each
sub-result back into a single merged `result` object. The web UI uses this to
load a whole page's data with one request. Each sub-call still names its own
`form` and `operation`, and the response merges their results under the
requested keys.

For SDK purposes, issuing one form per request is always valid and is what the
per-endpoint examples show.

---

## Authentication & session

1. Fetch RSA keys (`/login?form=auth`, `/login?form=keys`) — plaintext.
2. Send the encrypted login (`/login?form=login`) → receive `stok`.
3. Put `stok` in the URL path for every later call; increment `seq` per
   request.

Full details, including the `sign` string, the MD5 session hash and the
password RSA-encryption, are in [`../auth-protocol.md`](../auth-protocol.md)
and enumerated per form in [`../endpoints/login.md`](../endpoints/login.md).

The `stok` is also mirrored into a `sysauth=<stok>` cookie
(`Set-Cookie: sysauth=…`); the path parameter is what the dispatcher actually
checks.

---

## Plaintext endpoints

These skip the AES/RSA envelope and accept/return plain JSON.

| Endpoint | Purpose |
|----------|---------|
| `/login?form=auth` | RSA sign key + initial `seq`. |
| `/login?form=keys` | RSA password-encryption key. |
| `/login?form=check_factory_default` | Whether the unit is in factory state. |
| `/login?form=default_info` | Factory SSID / password / PIN. |
| `/admin/system?form=envar` | Environment variables. |
| `/admin/system?form=sysmode` | System mode. |
| `/admin/cloud?form=firmware` | Cloud firmware info. |
| `/admin/isp?form=isp_upgrade` | ISP-driven upgrade. |
| `/admin/firmware?form=config_multipart` | Firmware/config upload (multipart). |
| `/admin/log_export?form=save_log` | Log export download. |

> Some of these (e.g. `system?form=sysmode`, `isp?form=isp_upgrade`) are
> referenced by the app/SDK but not backed by a handler on every model; treat
> presence as model-dependent.

---

## Controller merge behaviour

Several `/admin/*` paths are served by **two** handler sets — one for the web
UI and one for the app — bound to the same URL. The dispatcher exposes the
union of their form tables at that single URL. This is why, for example,
`/admin/network` answers both the web forms (`wan_ipv4`, `internet`, …) and the
app-only forms (`lan_block`, `routes_static`, `mac_clone_list`, …).

The endpoint pages label each form **(web)**, **(app)** or **(both)**
accordingly.
</content>
