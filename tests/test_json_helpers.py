"""Unit tests for the typed JSON accessors in ``_json``."""

from __future__ import annotations

import pytest

from tplink_deco_api._json import (
    get_bool,
    get_float,
    get_int,
    get_object,
    get_str,
    get_str_tuple,
    loads,
)


def test_loads_object() -> None:
    assert loads(b'{"a": 1}') == {"a": 1}
    assert loads('{"b": 2}') == {"b": 2}


def test_loads_rejects_non_object() -> None:
    with pytest.raises(ValueError, match="top level is not an object"):
        loads(b"[1, 2, 3]")


def test_get_str() -> None:
    assert get_str({"k": "v"}, "k") == "v"
    assert get_str({"k": 5}, "k") == ""
    assert get_str({}, "k", default="fallback") == "fallback"


def test_get_int_from_bool() -> None:
    assert get_int({"k": True}, "k") == 1
    assert get_int({"k": False}, "k") == 0


def test_get_int_from_int_and_str() -> None:
    assert get_int({"k": 42}, "k") == 42
    assert get_int({"k": "17"}, "k") == 17


def test_get_int_bad_str_and_other_types() -> None:
    assert get_int({"k": "not-a-number"}, "k", default=-1) == -1
    assert get_int({"k": [1]}, "k", default=9) == 9
    assert get_int({}, "k", default=3) == 3


def test_get_float_variants() -> None:
    assert get_float({"k": True}, "k") == 1.0
    assert get_float({"k": 2}, "k") == 2.0
    assert get_float({"k": 1.5}, "k") == 1.5
    assert get_float({"k": "3.25"}, "k") == 3.25
    assert get_float({"k": "bad"}, "k", default=-1.0) == -1.0
    assert get_float({"k": [1]}, "k", default=7.0) == 7.0


def test_get_bool_variants() -> None:
    assert get_bool({"k": True}, "k") is True
    assert get_bool({"k": 0}, "k") is False
    assert get_bool({"k": 3}, "k") is True
    assert get_bool({"k": "yes"}, "k") is True
    assert get_bool({"k": "false"}, "k") is False
    assert get_bool({"k": [1]}, "k", default=True) is True


def test_get_object() -> None:
    assert get_object({"k": {"a": 1}}, "k") == {"a": 1}
    assert get_object({"k": "x"}, "k") == {}
    assert get_object({}, "k") == {}


def test_get_str_tuple() -> None:
    assert get_str_tuple({"k": ["a", "b", 3, None]}, "k") == ("a", "b")
    assert get_str_tuple({"k": ("x", "y")}, "k") == ("x", "y")
    assert get_str_tuple({"k": "scalar"}, "k") == ()
    assert get_str_tuple({}, "k") == ()
