"""Internal ``.env`` loader shared by the examples and the hardware test suite."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def load_env(env_file: Path) -> dict[str, str]:
    """Parse ``env_file`` into a mapping.

    Blank lines, comments and lines without ``=`` are ignored; a missing file
    yields an empty mapping.
    """
    if not env_file.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values
