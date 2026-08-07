"""Unit tests for the shared ``.env`` loader."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tplink_deco_api._env import load_env

if TYPE_CHECKING:
    from pathlib import Path


def test_load_env_missing_file(tmp_path: Path) -> None:
    assert load_env(tmp_path / ".env") == {}


def test_load_env_parses_and_skips_noise(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\n"
        "\n"
        "DECO_HOST = 192.168.0.1\n"
        "DECO_PASSWORD=secret=with=equals\n"
        "not a key value line\n"
    )
    assert load_env(env_file) == {
        "DECO_HOST": "192.168.0.1",
        "DECO_PASSWORD": "secret=with=equals",
    }
