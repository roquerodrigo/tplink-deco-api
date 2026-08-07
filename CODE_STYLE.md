# Code Style Guide

Style conventions for the `tplink-deco-api` Python SDK. Run
`uv run ruff format . && uv run ruff check . --fix && uv run mypy src` before
committing — all three must exit cleanly. `uv run pytest` follows.

**Always read this file before adding or restructuring code.**

## Language

- Code is written in **English**: file names, class names, function names,
  variable names, dictionary keys, identifier strings.
- The conversation language with the user can be Portuguese or anything else;
  what is committed to disk stays English.

## File organization

- **Source layout is `src/tplink_deco_api/`.** Tests in `tests/`, packaging in
  `pyproject.toml`. Hatchling is the build backend.
- **One top-level class per file.** Multiple semantically related classes get
  grouped into a package directory with one class per submodule and an
  `__init__.py` re-exporting the public symbols.
  - Example: `auth/` contains `transport.py`, `session.py`, `protocol.py`,
    plus `__init__.py`.
  - Example: `models/` contains `client_device.py`, `device.py`,
    `performance.py`, … plus `__init__.py`.
  - Example: `exceptions/` contains `api.py`, `crypto.py`, plus `__init__.py`.
- **Public surface goes through the package `__init__.py`.** Anything not
  re-exported there is internal — prefix with `_` if intended to stay private.
- **TypedDicts and `type` aliases do not count as "classes"** for this rule —
  they live alongside related code.
- **Leaf dataclasses parsed from a single payload may share a module.** A
  nested response shape (e.g. `wlan_config.py` with `WlanHost`, `WlanGuest`,
  `WlanBand`, …, or `wan_info.py` with `IpInfo`, `WanDetails`, `LanDetails`)
  stays in one module named after the top-level model; splitting each leaf
  into its own file would scatter one payload across many micro-files.
- **Helper functions** may live in the same file as the single class that
  uses them. Module-level private helpers are prefixed `_`.

## Naming

- Public classes are `CapWords`: `DecoClient`, `ClientDevice`, `Device`,
  `Performance`.
- Exception classes end with `Error`: `ApiError`, `CryptoError`.
- Module names are `snake_case`. Subpackages are organized by concern
  (`auth`, `models`, `exceptions`).
- Private attributes / functions are prefixed with `_`.

## Typing

**Strict typing. No `Any`, no bare collection generics.** Mypy enforces this.

Banned: `typing.Any`, `object` as a value type, bare `dict` / `list` /
`tuple` / `set`, `dict[str, Any]`.

Required:

- `@dataclass` for structured records (`ClientDevice`, `Device`,
  `Performance`, `LoginResult`, `SessionKeys`, …).
- Named `type` aliases for shared shapes.
- `frozenset[str]` / `tuple[str, ...]` for fixed string collections.
- Always type return values explicitly. Never rely on type inference for
  public APIs.
- Type-hinted module-level loggers: `log: logging.Logger = logging.getLogger(...)`.

The SDK ships a `py.typed` marker so downstream consumers get type info.

## Imports

- Always start every module with `from __future__ import annotations` so type
  hints become lazy strings.
- Same-package relative imports (`from .module import …`) are the default.
- Move type-only imports into a `TYPE_CHECKING` block:

  ```python
  from __future__ import annotations
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from collections.abc import Iterable
      from .models import ClientDevice
  ```

- `noqa` comments require a written justification inline. Never silence to
  "make ruff happy" — fix the underlying code.

## Docstrings

- Every public class, function, method (including `@property`) has a docstring.
- A single sentence is usually enough. Describe the *contract* or the *why*,
  not the obvious implementation.
- Module-level docstring at the top of every `.py` file.
- Avoid restating the type — the signature already does that.

## Comments

- Default to **no comments**. Add one only when the *why* is not obvious from
  the code: a hidden constraint, a workaround, a subtle invariant, a protocol
  reference.
- Never describe *what* the code does — well-named identifiers handle that.
- **No section dividers** like `# --- Auth helpers ---` to group related
  declarations. If a file has so many sections that you feel the need for
  visual separators, split it into multiple files instead.

## Logging

- Module-level logger: `log: logging.Logger = logging.getLogger("tplink_deco_api.<area>")`
  (e.g. `"tplink_deco_api.auth"`). Don't use `__name__` directly — the
  explicit dotted name lets users scope log levels precisely.
- Use **lazy `%`-formatting**, never f-strings:

  ```python
  log.debug("Login response: stok=%s", stok[:8] + "…")   # ✓ truncated secret
  log.debug(f"Login response: stok={stok}")              # ✗ leaks full token
  ```

- Levels:
  - `debug` — request/response counts, handshake steps.
  - `info` — successful login, key rotation.
  - `warning` — recoverable failures (single retry, fallback path).
  - `error` / `exception` — unrecoverable. `exception` inside `except` blocks
    captures the traceback.
- Never log raw `password`, full session cookies, or decrypted payloads.
  Truncate / hash if diagnostics need correlation.

## Error messages

- Format: `"Failed to <verb> <object>: <cause>"`. Keep them short and
  grep-able.
- Custom exceptions form a hierarchy rooted at `DecoError`, with four public
  subclasses: `ApiError` (non-zero `error_code` in a router response),
  `AuthenticationError` (login failure or missing session), `CryptoError`
  (RSA / AES / handshake primitives) and `TransportError` (HTTP failures).
  Wrap raw `OSError`, `socket` and `urllib` errors at the transport boundary
  so callers only catch this hierarchy.
- Pre-validate inputs before opening a socket so user-facing errors point at
  the bad input, not a downstream traceback.

## Public API surface

- Anything imported in the package `__init__.py` is the public contract
  (`DecoClient`, `ClientDevice`, `Device`, `Performance`, `ApiError`, …).
  Renaming or removing those symbols is a `BREAKING CHANGE:`.
- Internal modules can change shape freely as long as the public re-exports
  keep working.

## Pre-commit hooks

`pre-commit` is recommended. The repository ships `.pre-commit-config.yaml`
mirroring the lint commands; install once per clone:

```bash
pre-commit install
```

The hook runs the same gates as CI on every commit. Skip it only on
emergency `git commit --no-verify` and immediately re-run the lint commands.

## Conventional commits

All commits follow [Conventional Commits](https://www.conventionalcommits.org/),
in **English**, which `release-please` parses to bump `pyproject.toml` `version`
and generate `CHANGELOG.md`:

| Type | Meaning | Bump |
|---|---|---|
| `feat` | New feature | minor |
| `fix` | Bug fix | patch |
| `perf` | Performance improvement | patch |
| `deps` | Dependency bump | patch |
| `docs` | Documentation only | none |
| `refactor` | Refactor without behavior change | none |
| `test` | Test-only change | none |
| `ci` | CI / tooling change | none |
| `chore` | Anything else (rarely) | none |

- Subject line: imperative mood, lowercase, no trailing period.
- Use scopes when useful: `feat(auth): rotate session keys on 401`.
- A `BREAKING CHANGE:` footer (or `!` after type) bumps the major version.

## Packaging

- Build backend: `hatchling`. Wheel and sdist contain `src/tplink_deco_api`.
- `requires-python = ">=3.11"`. Don't bump this without a `BREAKING CHANGE:`
  footer.
- Public dependencies: keep them minimal and use `>=` lower bounds, not
  pins.
- The `[dependency-groups] dev` group carries test-only deps.
- A `py.typed` marker ships in the wheel so consumers see type info.

## Releasing

- `release-please` runs on `main` and opens a release-PR with the next
  version + `CHANGELOG.md`. Merging that PR triggers the publish job
  (the `publish-pypi` reusable workflow builds the sdist + wheel and uploads
  to PyPI authenticating with the `PYPI_API_TOKEN` repository secret).
- Don't manually edit `pyproject.toml` `version` — release-please owns it.

## Testing

- Tests live in `tests/`. `uv run pytest` runs the suite. Coverage is gated
  at **90%** (`--cov-fail-under=90` in `pyproject.toml`); keep the
  auth/crypto/transport layers covered since they're the byte-level surface
  most likely to regress silently.
- The default `uv run pytest` invocation is **network-free**. Hardware-dependent
  tests (real router connections, `tests/test_login.py`) are an opt-in
  integration suite: they are skipped during collection unless
  `--run-integration` is passed (or `DECO_INTEGRATION=1` is set), and even then
  the existing `DECO_PASSWORD` skipif keeps them dormant without credentials.
  Pure unit tests use captured byte fixtures and mock the HTTP layer at the
  transport boundary — never a real socket.

## Linting and verification

- Ruff configuration in `pyproject.toml` under `[tool.ruff]`. The rule set is
  `select = ["ALL"]`; the way to relax a rule is to add it to the curated
  `ignore` or `per-file-ignores` list **with the reason written next to it**,
  never a bare `noqa`.
- Mypy configuration in `pyproject.toml` under `[tool.mypy]` (strict, plus
  `warn_unreachable`, `warn_unused_ignores` and `disallow_any_explicit`).
- `requires-python`, the `Programming Language :: Python` classifiers,
  `[tool.ruff] target-version` and `[tool.mypy] python_version` describe the
  same floor and move together.
- Raise with the message bound to a local first — `message = "…"` followed by
  `raise SomeError(message)` — so tracebacks stay readable and the message is
  never built inside the `raise`.
- After every change run the three-step lint pipeline + `pytest`. Both
  gates mirror CI.
