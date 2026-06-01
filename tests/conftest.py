"""Pytest configuration: gate the live-hardware suite behind an opt-in flag.

The default ``uv run pytest`` invocation is network-free. The hardware
integration tests in ``tests/test_login.py`` hit a real Deco router and are
only collected when ``--run-integration`` is passed (or ``DECO_INTEGRATION=1``
is set in the environment).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterable

    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.nodes import Item

_INTEGRATION_FILE = "test_login.py"


def pytest_addoption(parser: Parser) -> None:
    """Register the ``--run-integration`` opt-in flag for the live-hardware suite."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run live-hardware integration tests (requires a reachable Deco router).",
    )


def pytest_configure(config: Config) -> None:
    """Register the ``integration`` marker so it is not reported as unknown."""
    config.addinivalue_line(
        "markers",
        "integration: live-hardware test, skipped unless --run-integration is given.",
    )


def pytest_collection_modifyitems(config: Config, items: Iterable[Item]) -> None:
    """Skip the live-hardware suite unless explicitly opted in."""
    if config.getoption("--run-integration") or os.environ.get("DECO_INTEGRATION") == "1":
        return
    skip = pytest.mark.skip(reason="live-hardware suite; pass --run-integration to enable")
    for item in items:
        if item.fspath.basename == _INTEGRATION_FILE:
            item.add_marker(skip)
