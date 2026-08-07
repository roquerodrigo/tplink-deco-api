# Login & session

Endpoints: **`/login`** and **`/domain_login`**. Most forms here are
[plaintext](../protocol/transport-and-dispatch.md#plaintext-endpoints); only
`login` itself carries the encrypted envelope.

The end-to-end handshake (AES key derivation, `sign`, `seq`, MD5 session hash)
is specified in [`../auth-protocol.md`](../auth-protocol.md). This page
enumerates the individual forms.

---

## `/login?form=auth` — RSA sign key + seq

**Operation:** `read` · **Auth:** plaintext

```json
{ "operation": "read" }
```

Response:
```json
{ "result": { "key": ["<modulus_hex>", "010001"], "seq": 766218342 }, "error_code": 0 }
```

- `key` — 512-bit RSA public key `[n, e]` used to build the `sign` field on
  every subsequent request.
- `seq` — session nonce folded into every request signature as
  `seq + len(data_b64)`; the SDK reuses the handshake value unchanged.

## `/login?form=keys` — password RSA key

**Operation:** `read` · **Auth:** plaintext

```json
{ "operation": "read" }
```

Response:
```json
{ "result": { "username": "", "password": ["<modulus_hex>", "010001"] }, "error_code": 0 }
```

- `password` — 1024-bit RSA public key `[n, e]` used to encrypt the account
  password inside the login payload.

## `/login?form=login` — authenticate

**Operation:** `login` · **Auth:** encrypted envelope (with AES key in the
signature, `isLogin=true`)

Decrypted `data`:
```json
{ "operation": "login", "params": { "password": "<RSA(pwd)>" } }
```

Response:
```json
{ "result": { "stok": "abe375823d4f46ce569b533fed43f0a2", "usr_lvl": 1 }, "error_code": 0 }
```

- `stok` — session token; placed in the URL path (`;stok=<stok>`) for every
  authenticated call and mirrored as a `sysauth` cookie.
- `usr_lvl` — privilege level (`1` = admin).

Example: [`../api-responses/login.json`](../api-responses/login.json).

The server enforces an attempt counter (`failureCount`, `attemptsAllowed`); too
many failures throttle further attempts.

## `/login?form=check_factory_default`

**Operation:** `read` · **Auth:** plaintext

Returns whether the unit is still at factory defaults (never configured). Used
to decide between the onboarding flow and normal login.

## `/login?form=default_info`

**Operation:** `read` · **Auth:** plaintext

Returns the factory-printed identity:

- `default_ssid` — factory SSID, `Deco_XXXX` (last MAC bytes).
- `default_pwd` — factory Wi-Fi password.
- `PIN` — factory WPS PIN.

## `/login?form=mini_login`, `/login?form=cloud_login`

**Operation:** `login` · **Auth:** encrypted

Alternate login paths:

- `mini_login` — reduced local login (used in constrained states, e.g. during
  onboarding).
- `cloud_login` — validates a TP-Link cloud credential against the locally
  cached cloud password instead of the local admin password.

Both return the same `{ stok, usr_lvl }` shape as `login`.

---

## `/domain_login?form=dlogin`

**Operations:** read / write · **Auth:** encrypted

Domain (hostname-based) login used when reaching the router by its local domain
name rather than IP. Behaves like `login` but keyed to the domain-access path;
`tips_cancel` dismisses the domain-login hint.

---

## Session lifecycle

1. `auth` + `keys` (plaintext, parallel) → RSA keys + `seq`.
2. Client derives a random AES key/IV, computes `MD5(username+password)`.
3. `login` (encrypted) → `stok`.
4. Every later call: URL carries `;stok=<stok>`, body is enveloped, and the
   signature embeds the handshake `seq` plus the payload length.
5. `logout` — [`/admin/system?form=logout`](./system.md) drops the session;
   the SDK simply discards the token client-side.
</content>
