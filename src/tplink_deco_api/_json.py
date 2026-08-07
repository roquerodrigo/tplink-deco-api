"""Typed JSON aliases and safe accessors for router payloads."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import TYPE_CHECKING, TypeAlias, cast

if TYPE_CHECKING:
    from collections.abc import Sequence

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = "JsonPrimitive | Sequence[JsonValue] | Mapping[str, JsonValue]"
JsonObject: TypeAlias = Mapping[str, JsonValue]


def loads(payload: bytes | str) -> JsonObject:
    """Parse a JSON object response, rejecting non-object top levels."""
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        message = "Failed to parse JSON: top level is not an object"
        raise ValueError(message)
    return cast("JsonObject", parsed)


def get_str(data: JsonObject, key: str, default: str = "") -> str:
    """Return ``data[key]`` if it is a string, else ``default``."""
    value = data.get(key, default)
    return value if isinstance(value, str) else default


def get_int(data: JsonObject, key: str, default: int = 0) -> int:
    """Return ``data[key]`` coerced to int, falling back to ``default``."""
    value = data.get(key, default)
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def get_float(data: JsonObject, key: str, default: float = 0.0) -> float:
    """Return ``data[key]`` coerced to float, falling back to ``default``."""
    value = data.get(key, default)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def get_bool(data: JsonObject, key: str, default: bool = False) -> bool:
    """Return ``data[key]`` coerced to bool, falling back to ``default``."""
    value = data.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes"}
    return default


def get_object(data: JsonObject, key: str) -> JsonObject:
    """Return ``data[key]`` as a JSON object, or an empty mapping."""
    value = data.get(key)
    return value if isinstance(value, Mapping) else {}


def get_str_tuple(data: JsonObject, key: str) -> tuple[str, ...]:
    """Return ``data[key]`` as a tuple of strings, dropping non-strings."""
    value = data.get(key)
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, str))
