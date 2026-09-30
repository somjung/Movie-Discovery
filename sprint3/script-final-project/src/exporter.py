"""CSV export of the user's lists (watchlist and favorites)."""

import csv
import os

LIST_COLUMNS = ("tmdb_id", "title", "release_date", "vote_average", "note")
# Both lists share the same export schema; the old name stays for safety.
WATCHLIST_COLUMNS = LIST_COLUMNS


class ExportError(Exception):
    """Raised when a list cannot be written to disk."""


class Exporter:
    """Writes project data to CSV files."""

    @staticmethod
    def _write_rows(rows, path, columns):
        """Write ``rows`` to ``path``, creating the folder chain first.

        Raises ExportError (naming the failing path) when writing fails.
        """
        try:
            folder = os.path.dirname(os.path.abspath(path))
            os.makedirs(folder, exist_ok=True)
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(columns)
                for row in rows:
                    writer.writerow([
                        "" if row.get(column) is None else row.get(column)
                        for column in columns
                    ])
        except OSError as exc:
            raise ExportError(f"cannot write {path}: {exc}") from exc

    @staticmethod
    def export_watchlist(store, path):
        """Write the current watchlist to ``path``; return how many rows."""
        rows = store.get_watchlist()
        Exporter._write_rows(rows, path, LIST_COLUMNS)
        return len(rows)

    @staticmethod
    def export_favorites(store, path):
        """Write the current favorites to ``path``; return how many rows."""
        rows = store.get_favorites()
        Exporter._write_rows(rows, path, LIST_COLUMNS)
        return len(rows)
