"""Unit tests for the interactive CLI.

Inputs are scripted and the services are injected as offline fakes, so
every edge case from the PLAN.md Definition of Done is verified without a
real terminal, network, or database file.
"""

import pytest

from fakes import FakeTmdbClient
from src.cli import CLI
from src.movie_store import MovieStore
from src.sample_data import SAMPLE_MOVIES


def scripted_inputs(lines):
    """Return an input function that replays the given lines, then EOF."""
    queue = list(lines)

    def fake_input(prompt=""):
        if not queue:
            raise EOFError
        return queue.pop(0)

    return fake_input


def run_cli(lines, data_dir=None):
    """Run the CLI with scripted input and fake services; return (outputs, cli)."""
    outputs = []
    cli = CLI(input_func=scripted_inputs(lines), output_func=outputs.append,
              client=FakeTmdbClient(), store=MovieStore(":memory:"),
              data_dir=data_dir)
    cli.run()
    return outputs, cli


def joined(outputs):
    return "\n".join(outputs)


@pytest.mark.parametrize("command", ["quit", "QUIT", "Quit", "  quit  ",
                                     "exit", "q", "ออก"])
def test_quit_variants_exit_with_farewell(command):
    outputs, cli = run_cli([command])
    assert "ลาก่อน" in joined(outputs)
    assert cli.running is False


def test_eof_exits_gracefully():
    outputs, cli = run_cli([])
    assert "ลาก่อน" in joined(outputs)
    assert cli.running is False


def test_empty_input_warns_and_continues():
    outputs, _ = run_cli(["", "quit"])
    assert "กรุณาพิมพ์คำสั่ง" in joined(outputs)
    assert "ลาก่อน" in joined(outputs)


def test_unknown_command_warns_and_recovers():
    outputs, _ = run_cli(["asdf", "quit"])
    text = joined(outputs)
    assert "ไม่รู้จักคำสั่ง" in text
    assert "help" in text
    assert "ลาก่อน" in text


def test_search_requires_a_title():
    outputs, _ = run_cli(["search", "quit"])
    assert "ต้องระบุชื่อเรื่อง" in joined(outputs)


def test_search_finds_sample_movie():
    outputs, _ = run_cli(["search alpha", "quit"])
    assert "Alpha Signal" in joined(outputs)


def test_search_is_case_insensitive():
    outputs, _ = run_cli(["SEARCH ALPHA", "quit"])
    assert "Alpha Signal" in joined(outputs)


def test_discover_rejects_non_numeric_id():
    outputs, _ = run_cli(["discover abc", "quit"])
    assert "ต้องเป็นตัวเลข" in joined(outputs)


def test_discover_rejects_zero_and_negative():
    outputs, _ = run_cli(["discover 0", "discover -3", "quit"])
    assert joined(outputs).count("ต้องมากกว่า 0") == 2


def test_discover_unknown_seed_is_reported():
    outputs, _ = run_cli(["discover 999", "quit"])
    assert "ไม่พบรหัสภาพยนตร์ 999" in joined(outputs)


def test_watchlist_add_list_and_duplicate():
    outputs, cli = run_cli(
        ["watchlist add 101", "watchlist list", "watchlist add 101", "quit"]
    )
    text = joined(outputs)
    assert "เพิ่ม 'Alpha Signal'" in text
    assert "อยู่ในรายการรับชมแล้ว" in text
    assert len(cli.store.get_watchlist()) == 1


def test_watchlist_needs_subcommand():
    outputs, _ = run_cli(["watchlist", "quit"])
    assert "ต้องมีคำสั่งย่อย" in joined(outputs)


def test_help_shows_menu():
    outputs, _ = run_cli(["help", "quit"])
    text = joined(outputs)
    assert "search" in text
    assert "quit" in text


def test_prompt_marker_is_stable():
    prompts = []

    def capture(prompt=""):
        prompts.append(prompt)
        raise EOFError

    cli = CLI(input_func=capture, output_func=lambda *_: None,
              client=FakeTmdbClient(), store=MovieStore(":memory:"))
    cli.run()
    assert prompts and all(prompt == "movie> " for prompt in prompts)


# ---------- Sprint 2: favorites, export, history, flags, missing key ----------


def test_favorites_lifecycle():
    outputs, cli = run_cli(
        ["favorites add 101", "favorites add 101", "favorites list",
         "favorites remove 101", "favorites remove 101", "quit"]
    )
    text = joined(outputs)
    assert "เพิ่ม 'Alpha Signal' เข้ารายการโปรดแล้ว" in text
    assert text.count("อยู่ในรายการโปรดแล้ว") == 1
    assert "รายการโปรด (1 เรื่อง):" in text
    assert "นำ 'Alpha Signal' ออกจากรายการโปรดแล้ว" in text
    assert "ไม่พบรหัสภาพยนตร์ 101 ในรายการโปรด" in text
    assert cli.store.get_favorites() == []


def test_export_writes_csv_to_data_dir(tmp_path):
    outputs, _ = run_cli(
        ["watchlist add 101", "favorites add 102",
         "export watchlist", "export favorites", "quit"],
        data_dir=str(tmp_path)
    )
    text = joined(outputs)
    watch = tmp_path / "watchlist.csv"
    favorites = tmp_path / "favorites.csv"
    assert f"ส่งออก 1 รายการไปที่ {watch}" in text
    assert f"ส่งออก 1 รายการไปที่ {favorites}" in text
    assert "Alpha Signal" in watch.read_text(encoding="utf-8")


def test_export_requires_a_list_name():
    outputs, _ = run_cli(["export wrong", "export", "quit"])
    assert joined(outputs).count("ต้องระบุรายการ") == 2


def test_history_reports_recent_searches():
    outputs, _ = run_cli(["search alpha", "search bravo", "history",
                          "history 1", "quit"])
    text = joined(outputs)
    assert "ประวัติการค้นหาล่าสุด (2 รายการ):" in text
    assert "'alpha'" in text and "'bravo'" in text
    assert text.count("(1 รายการ):") == 1


def test_history_empty_message():
    outputs, _ = run_cli(["history", "quit"])
    assert "ยังไม่มีประวัติการค้นหา" in joined(outputs)


def test_watchlist_remove_and_clear():
    outputs, cli = run_cli(
        ["watchlist add 101", "watchlist remove 101", "watchlist remove 101",
         "watchlist clear", "quit"]
    )
    text = joined(outputs)
    assert "นำ 'Alpha Signal' ออกจากรายการรับชมแล้ว" in text
    assert "ไม่พบรหัสภาพยนตร์ 101 ในรายการรับชม" in text
    assert "ล้างรายการรับชมเรียบร้อยแล้ว (0 เรื่อง)" in text
    assert cli.store.get_watchlist() == []


@pytest.mark.parametrize("command,expected", [
    ("discover 101 --min-rating 11", "ต้องอยู่ระหว่าง 0 ถึง 10"),
    ("discover 101 --min-rating abc", "ต้องเป็นตัวเลข"),
    ("discover 101 --min-votes -5", "ต้องไม่ติดลบ"),
    ("discover 101 --min-votes x", "จำนวนเต็ม"),
    ("discover 101 --year 19x0", "4 หลัก"),
    ("discover 101 --year 2020-1990", "ช่วงปีต้องเรียง"),
    ("discover 101 --sort banana", "--sort ต้องเป็น"),
    ("discover 101 --limit 0", "ต้องมากกว่า 0"),
    ("discover 101 --limit x", "ต้องเป็นตัวเลข"),
    ("discover 101 --bogus 1", "ไม่รู้จักตัวเลือก"),
    ("discover 101 --limit", "ต้องมีค่าตามหลัง"),
])
def test_discover_option_validation(command, expected):
    outputs, _ = run_cli([command, "quit"])
    assert expected in joined(outputs)


def test_discover_sort_and_limit_applied():
    outputs, _ = run_cli(["discover 101 --sort votes --limit 2", "quit"])
    text = joined(outputs)
    assert "เรียงตาม votes" in text
    assert "[103]" in text and "[101]" in text and "[105]" not in text


def test_discover_year_sort_puts_unknown_last():
    outputs, _ = run_cli(["discover 101 --sort year", "quit"])
    text = joined(outputs)
    assert "1. [105]" in text and "5. [104]" in text


def test_missing_key_guides_and_keeps_offline_commands(
        monkeypatch, tmp_path):
    monkeypatch.delenv("TMDB_API_KEY", raising=False)
    outputs = []
    cli = CLI(input_func=scripted_inputs(
                  ["search alpha", "discover 101", "watchlist add 999",
                   "watchlist list", "history", "quit"]),
              output_func=outputs.append, store=MovieStore(":memory:"),
              data_dir=str(tmp_path))
    cli.run()
    text = joined(outputs)
    assert cli.key_missing is True
    assert text.count("ยังไม่ได้ตั้งค่าคีย์ TMDB") == 3
    assert "รายการรับชมยังว่างอยู่" in text
    assert "ยังไม่มีประวัติการค้นหา" in text


def test_offline_add_works_for_stored_movies(monkeypatch):
    monkeypatch.delenv("TMDB_API_KEY", raising=False)
    outputs = []
    store = MovieStore(":memory:")
    store.add_movie(dict(SAMPLE_MOVIES[0]))
    cli = CLI(input_func=scripted_inputs(["watchlist add 101",
                                          "watchlist list", "quit"]),
              output_func=outputs.append, store=store)
    cli.run()
    text = joined(outputs)
    assert "เพิ่ม 'Alpha Signal' เข้ารายการรับชมแล้ว" in text
    assert "[101] Alpha Signal" in text


def test_help_covers_sprint2_commands():
    outputs, _ = run_cli(["help", "quit"])
    text = joined(outputs)
    for command in ("favorites", "export", "history"):
        assert command in text
