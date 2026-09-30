"""Entry point for the interactive Movie Discovery CLI.

Run with:

    python -m src.app
"""

from .cli import CLI


def main():
    """Start the interactive CLI."""
    CLI().run()


if __name__ == "__main__":
    main()
