"""Unit tests for the interactive CLI (Sprint 1 front-end).

Inputs are scripted (injected), so every edge case from the PLAN.md
Definition of Done is verified without a real terminal.
"""

import pytest

from src.cli import CLI


def scripted_inputs(lines):
    """Return an input function that replays the given lines, then EOF."""
    queue = list(lines)

    def fake_input(prompt=""):
        if not queue:
            raise EOFError
        return queue.pop(0)

    return fake_input


def run_cli(lines):
    """Run the CLI with scripted input; return (outputs, cli)."""
    outputs = []
    cli = CLI(input_func=scripted_inputs(lines), output_func=outputs.append)
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
    assert len(cli.watchlist) == 1


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

    cli = CLI(input_func=capture, output_func=lambda *_: None)
    cli.run()
    assert prompts and all(prompt == "movie> " for prompt in prompts)
