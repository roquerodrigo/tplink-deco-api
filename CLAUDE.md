# tplink-deco-api

Python SDK for accessing and controlling **TP-Link Deco** mesh Wi-Fi routers
via the internal HTTP API. The Deco API uses proprietary RSA/AES
authentication. Goal: programmatic automation without relying on the
official app.

## Always read `CODE_STYLE.md` first

Before creating, renaming or restructuring any file/class/function, **read
[`CODE_STYLE.md`](./CODE_STYLE.md)**. It is the single source of truth for
conventions: language, file organisation, naming, typing, imports,
docstrings, comments, logging, error messages, public API surface,
pre-commit hooks, conventional commits, packaging, releasing, testing,
lint workflow.

## Verification workflow

After every code change, always run lint then tests, in that order, before
declaring the task done:

```bash
uv run ruff format . && uv run ruff check . --fix && uv run mypy src
uv run pytest
```

Both gates mirror CI. Skip this only when the change literally cannot
affect lint or tests (e.g., README-only edits).

## Downstream consumer

The sibling repo `ha-tplink-deco` (Home Assistant integration) depends on
this SDK, pinned with `==` in both its `pyproject.toml` and its
`manifest.json` (the two pins can drift — check both when bumping). Renaming
or removing any symbol re-exported from `tplink_deco_api/__init__.py` breaks
that integration and requires a coordinated version bump there.
