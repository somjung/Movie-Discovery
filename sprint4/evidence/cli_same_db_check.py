"""DoD proof: the CLI sees the same database the web app just wrote to.

Runs the real CLI with scripted input (same pattern as the test suite)
against the project database and prints the watchlist rows.

Run (from anywhere, with the project's venv python):
    PYTHONUTF8=1 python cli_same_db_check.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "script-final-project"
sys.path.insert(0, str(ROOT))

from src.cli import CLI  # noqa: E402
from src.config import get_db_path  # noqa: E402

lines = iter(["watchlist list"])
outputs = []


def scripted_input(prompt=""):
    try:
        return next(lines)
    except StopIteration:
        raise EOFError


cli = CLI(input_func=scripted_input, output_func=outputs.append)
cli.run()

print("=== CLI output (scripted session: watchlist list) ===")
print("\n".join(str(part) for part in outputs))
print("=== database used ===")
print(get_db_path())
