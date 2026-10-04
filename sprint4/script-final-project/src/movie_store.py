"""SQLite persistence layer: movies, similar-links, watchlist, favorites,
search history, and the TMDB response cache.
"""

import os
import sqlite3

# How long a cached TMDB response stays fresh (24 hours, in seconds).
CACHE_TTL_SECONDS = 24 * 60 * 60

SCHEMA = """
CREATE TABLE IF NOT EXISTS movies (
    tmdb_id      INTEGER PRIMARY KEY,
    title        TEXT NOT NULL,
    release_date TEXT,
    vote_average REAL,
    vote_count   INTEGER,
    popularity   REAL,
    overview     TEXT,
    added_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS similar_links (
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    score     REAL,
    PRIMARY KEY (source_id, target_id)
);

CREATE TABLE IF NOT EXISTS watchlist (
    movie_id INTEGER PRIMARY KEY,
    note     TEXT,
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS favorites (
    movie_id INTEGER PRIMARY KEY,
    note     TEXT,
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS searches (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    query        TEXT NOT NULL,
    result_count INTEGER NOT NULL DEFAULT 0,
    searched_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS api_cache (
    cache_key  TEXT PRIMARY KEY,
    payload    TEXT NOT NULL,
    fetched_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class MovieStore:
    """Small data-access layer on top of SQLite."""

    def __init__(self, db_path=":memory:"):
        """Open a connection and create the tables when they do not exist yet."""
        if db_path != ":memory:":
            parent = os.path.dirname(os.path.abspath(db_path))
            os.makedirs(parent, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def close(self):
        """Close the underlying database connection."""
        self.conn.close()

    def init_db(self):
        """Create the tables when they do not exist yet."""
        with self.conn:
            self.conn.executescript(SCHEMA)

    def add_movie(self, movie):
        """Insert a movie (or refresh it when the id already exists)."""
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO movies (tmdb_id, title, release_date, vote_average,
                                    vote_count, popularity, overview)
                VALUES (:tmdb_id, :title, :release_date, :vote_average,
                        :vote_count, :popularity, :overview)
                ON CONFLICT(tmdb_id) DO UPDATE SET
                    title = excluded.title,
                    release_date = excluded.release_date,
                    vote_average = excluded.vote_average,
                    vote_count = excluded.vote_count,
                    popularity = excluded.popularity,
                    overview = excluded.overview
                """,
                {
                    "tmdb_id": movie["id"],
                    "title": movie.get("title", ""),
                    "release_date": movie.get("release_date") or "",
                    "vote_average": movie.get("vote_average") or 0.0,
                    "vote_count": movie.get("vote_count") or 0,
                    "popularity": movie.get("popularity") or 0.0,
                    "overview": movie.get("overview") or "",
                },
            )
        return movie["id"]

    def get_movie(self, tmdb_id):
        """Return one movie as a dict, or None when it is not stored."""
        row = self.conn.execute(
            "SELECT * FROM movies WHERE tmdb_id = ?", (tmdb_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_movies(self):
        """All stored movies (most recently added first)."""
        rows = self.conn.execute(
            "SELECT * FROM movies ORDER BY added_at DESC, tmdb_id"
        ).fetchall()
        return [dict(row) for row in rows]

    def add_similar_link(self, source_id, target_id, score=None):
        """Record that ``target_id`` is similar to ``source_id``."""
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO similar_links (source_id, target_id, score)
                VALUES (?, ?, ?)
                ON CONFLICT(source_id, target_id) DO UPDATE SET
                    score = excluded.score
                """,
                (source_id, target_id, score),
            )

    def get_similar_links(self, source_id):
        """Similar-movie links recorded for a source movie (best first)."""
        rows = self.conn.execute(
            """
            SELECT target_id, score FROM similar_links
            WHERE source_id = ? ORDER BY score DESC
            """,
            (source_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def add_to_watchlist(self, movie_id, note=None):
        """Add a movie to the watchlist (no duplicates)."""
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO watchlist (movie_id, note) VALUES (?, ?)
                ON CONFLICT(movie_id) DO UPDATE SET note = excluded.note
                """,
                (movie_id, note),
            )

    def is_in_watchlist(self, movie_id):
        """True when the movie id is already on the watchlist."""
        row = self.conn.execute(
            "SELECT 1 FROM watchlist WHERE movie_id = ?", (movie_id,)
        ).fetchone()
        return row is not None

    def get_watchlist(self):
        """Watchlist rows joined with movie details (newest first)."""
        rows = self.conn.execute(
            """
            SELECT w.movie_id AS tmdb_id, m.title, m.release_date,
                   m.vote_average, w.note, w.added_at
            FROM watchlist w
            LEFT JOIN movies m ON m.tmdb_id = w.movie_id
            ORDER BY w.added_at DESC, w.movie_id
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def remove_from_watchlist(self, movie_id):
        """Delete one watchlist row; return True when a row was removed."""
        with self.conn:
            cur = self.conn.execute(
                "DELETE FROM watchlist WHERE movie_id = ?", (movie_id,)
            )
        return cur.rowcount > 0

    def clear_watchlist(self):
        """Delete every watchlist row; return how many entries were removed."""
        with self.conn:
            cur = self.conn.execute("DELETE FROM watchlist")
        return cur.rowcount

    def add_favorite(self, movie_id, note=None):
        """Add a movie to favorites (no duplicates; refreshes the note)."""
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO favorites (movie_id, note) VALUES (?, ?)
                ON CONFLICT(movie_id) DO UPDATE SET note = excluded.note
                """,
                (movie_id, note),
            )

    def is_in_favorites(self, movie_id):
        """True when the movie id is already in favorites."""
        row = self.conn.execute(
            "SELECT 1 FROM favorites WHERE movie_id = ?", (movie_id,)
        ).fetchone()
        return row is not None

    def get_favorites(self):
        """Favorite rows joined with movie details (newest first)."""
        rows = self.conn.execute(
            """
            SELECT f.movie_id AS tmdb_id, m.title, m.release_date,
                   m.vote_average, f.note, f.added_at
            FROM favorites f
            LEFT JOIN movies m ON m.tmdb_id = f.movie_id
            ORDER BY f.added_at DESC, f.movie_id
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def remove_favorite(self, movie_id):
        """Delete one favorites row; return True when a row was removed."""
        with self.conn:
            cur = self.conn.execute(
                "DELETE FROM favorites WHERE movie_id = ?", (movie_id,)
            )
        return cur.rowcount > 0

    def record_search(self, query, result_count):
        """Append one search to the history (query text + number of results)."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO searches (query, result_count) VALUES (?, ?)",
                (query, result_count),
            )

    def get_recent_searches(self, limit=10):
        """Return the most recent searches first, up to ``limit`` rows."""
        rows = self.conn.execute(
            """
            SELECT id, query, result_count, searched_at FROM searches
            ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_cached(self, cache_key, ttl_seconds=CACHE_TTL_SECONDS):
        """Return a cached payload younger than the TTL, or None on a miss."""
        row = self.conn.execute(
            """
            SELECT payload FROM api_cache
            WHERE cache_key = ? AND fetched_at >= datetime('now', ?)
            """,
            (cache_key, f"-{max(0, int(ttl_seconds))} seconds"),
        ).fetchone()
        return row["payload"] if row else None

    def save_cached(self, cache_key, payload):
        """Store (or refresh) a response payload under ``cache_key``."""
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO api_cache (cache_key, payload) VALUES (?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    payload = excluded.payload,
                    fetched_at = datetime('now')
                """,
                (cache_key, payload),
            )
