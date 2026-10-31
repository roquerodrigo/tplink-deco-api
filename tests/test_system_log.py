"""Network-free tests for reading the gateway's system log."""

from __future__ import annotations

from unittest.mock import call, patch

from tplink_deco_api import DecoClient, SystemLogEntry, SystemLogPage

_RAW_LINE = "Mon Oct 26 13:57:02 2026 daemon.notice pppd[18932]: len < 0"


def _read(index: int) -> object:
    return call(
        "admin/log_export",
        "feedback_log",
        {"operation": "read", "params": {"index": index, "limit": 100}},
    )


def _build(level: int) -> object:
    return call(
        "admin/log_export",
        "feedback_log",
        {"operation": "build", "params": {"level": level}},
    )


def test_entry_splits_a_raw_syslog_line() -> None:
    assert SystemLogEntry.from_api({"time": "", "level": "", "content": _RAW_LINE}) == (
        SystemLogEntry(
            time="Mon Oct 26 13:57:02 2026",
            facility="daemon",
            level="notice",
            source="pppd[18932]",
            message="len < 0",
        )
    )


def test_entry_splits_a_line_without_a_process_name() -> None:
    line = "Mon Oct 26 15:47:19 2026 user.emerg : tp215,22[2338]:"
    entry = SystemLogEntry.from_api({"content": line})
    assert (entry.facility, entry.level, entry.source) == ("user", "emerg", "")
    assert entry.message == "tp215,22[2338]:"


def test_entry_keeps_structured_fields() -> None:
    payload = {"time": "12:38:31", "level": "INFO", "type": "PPP", "content": "PPPoE up"}
    assert SystemLogEntry.from_api(payload) == SystemLogEntry(
        time="12:38:31", facility="", level="INFO", source="PPP", message="PPPoE up"
    )


def test_entry_keeps_an_unrecognized_line_as_the_message() -> None:
    entry = SystemLogEntry.from_api({"content": "free text"})
    assert entry.message == "free text"
    assert entry.time == ""


def test_page_skips_items_that_are_not_objects() -> None:
    page = SystemLogPage.from_api(2, {"logList": [{"content": "ok"}, "junk"], "totalNum": 3})
    assert page.page == 2
    assert page.total_pages == 3
    assert [entry.message for entry in page.entries] == ["ok"]


def test_page_tolerates_a_malformed_payload() -> None:
    assert SystemLogPage.from_api(0, {"logList": "unexpected"}) == SystemLogPage(0, 0, ())


def test_get_system_log_reads_the_newest_page_by_default() -> None:
    client = DecoClient("192.0.2.1", "admin", "secret")
    responses = [
        {},
        {"logList": [{"content": "old"}], "totalNum": 3},
        {"logList": [{"content": "new"}], "totalNum": 3},
    ]
    with patch.object(client, "request", side_effect=responses) as request:
        page = client.get_system_log(5)

    assert request.call_args_list == [_build(5), _read(0), _read(2)]
    assert page.page == 2
    assert [entry.message for entry in page.entries] == ["new"]


def test_get_system_log_reads_once_when_there_is_a_single_page() -> None:
    client = DecoClient("192.0.2.1", "admin", "secret")
    responses = [{}, {"logList": [{"content": "only"}], "totalNum": 1}]
    with patch.object(client, "request", side_effect=responses) as request:
        page = client.get_system_log(8)

    assert request.call_args_list == [_build(8), _read(0)]
    assert page.page == 0


def test_get_system_log_reads_a_chosen_page() -> None:
    client = DecoClient("192.0.2.1", "admin", "secret")
    responses = [{}, {"logList": [{"content": "middle"}], "totalNum": 3}]
    with patch.object(client, "request", side_effect=responses) as request:
        page = client.get_system_log(5, page=1)

    assert request.call_args_list == [_build(5), _read(1)]
    assert page.page == 1
