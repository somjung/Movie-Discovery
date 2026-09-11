"""CSV export helpers."""

import csv

WATCHLIST_COLUMNS = ("tmdb_id", "title", "release_date", "vote_average", "note")


class Exporter:
    """Writes project data to CSV files."""

    @staticmethod
    def export_watchlist(store, path):
        """Write the current watchlist to ``path`` and return the path."""
        rows = store.get_watchlist()
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(WATCHLIST_COLUMNS)
            for row in rows:
                writer.writerow([
                    "" if row.get(column) is None else row.get(column)
                    for column in WATCHLIST_COLUMNS
                ])
        return path
