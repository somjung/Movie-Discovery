"""Unit tests for the SQLite persistence layer."""

import pytest

from src.movie_store import CACHE_TTL_SECONDS, MovieStore


@pytest.fixture()
def store(tmp_path):
    db = MovieStore(str(tmp_path / "test.db"))
    yield db
    db.close()


def movie(movie_id=101, title="Alpha Signal", rating=7.5):
    return {"id": movie_id, "title": title, "release_date": "2010-05-01",
            "vote_average": rating, "vote_count": 100, "popularity": 5.0}


def test_add_and_get_movie_roundtrip(store):
    store.add_movie(movie())
    stored = store.get_movie(101)
    assert stored["title"] == "Alpha Signal"
    assert stored["vote_average"] == 7.5


def test_upsert_refreshes_existing_movie(store):
    store.add_movie(movie(rating=7.5))
    store.add_movie(movie(rating=9.1))
    assert len(store.list_movies()) == 1
    assert store.get_movie(101)["vote_average"] == 9.1


def test_missing_movie_returns_none(store):
    assert store.get_movie(999) is None


def test_similar_link_roundtrip(store):
    store.add_similar_link(1, 101, score=8.0)
    store.add_similar_link(1, 102, score=6.0)
    links = store.get_similar_links(1)
    assert [link["target_id"] for link in links] == [101, 102]


def test_watchlist_add_list_and_flag(store):
    store.add_movie(movie())
    assert store.is_in_watchlist(101) is False
    store.add_to_watchlist(101, note="watch soon")
    assert store.is_in_watchlist(101) is True
    rows = store.get_watchlist()
    assert rows[0]["title"] == "Alpha Signal"
    assert rows[0]["note"] == "watch soon"


def test_store_creates_parent_directory(tmp_path):
    nested = tmp_path / "nested" / "dir" / "movies.db"
    db = MovieStore(str(nested))
    db.add_movie(movie())
    db.close()
    assert nested.exists()


# ---------- Sprint 2: watchlist removals, favorites, searches, cache ----------


def test_watchlist_remove_returns_true_then_false(store):
    store.add_movie(movie())
    store.add_to_watchlist(101)
    assert store.remove_from_watchlist(101) is True
    assert store.remove_from_watchlist(101) is False
    assert store.get_watchlist() == []


def test_watchlist_clear_reports_removed_count(store):
    store.add_movie(movie(101))
    store.add_movie(movie(102, title="Bravo Horizon"))
    store.add_to_watchlist(101)
    store.add_to_watchlist(102)
    assert store.clear_watchlist() == 2
    assert store.clear_watchlist() == 0
    assert store.get_watchlist() == []


def test_favorites_roundtrip_and_note_refresh(store):
    store.add_movie(movie())
    assert store.is_in_favorites(101) is False
    store.add_favorite(101, note="top pick")
    assert store.is_in_favorites(101) is True
    rows = store.get_favorites()
    assert rows[0]["title"] == "Alpha Signal"
    assert rows[0]["note"] == "top pick"
    store.add_favorite(101, note="changed")
    assert store.get_favorites()[0]["note"] == "changed"
    assert store.remove_favorite(101) is True
    assert store.remove_favorite(101) is False


def test_recent_searches_newest_first_with_limit(store):
    store.record_search("alpha", 3)
    store.record_search("bravo", 5)
    store.record_search("cobalt", 0)
    rows = store.get_recent_searches(2)
    assert [row["query"] for row in rows] == ["cobalt", "bravo"]
    assert rows[0]["result_count"] == 0
    assert rows[0]["searched_at"]
    assert len(store.get_recent_searches()) == 3


def test_cache_roundtrip_and_expiry(store):
    assert store.get_cached("k") is None
    store.save_cached("k", '{"a": 1}')
    assert store.get_cached("k") == '{"a": 1}'
    store.conn.execute(
        "UPDATE api_cache SET fetched_at = datetime('now', '-2 days') "
        "WHERE cache_key = 'k'"
    )
    store.conn.commit()
    assert store.get_cached("k") is None


def test_cache_save_overwrites_previous_payload(store):
    store.save_cached("k", "old")
    store.save_cached("k", "new")
    assert store.get_cached("k") == "new"


def test_cache_ttl_constant_is_24_hours():
    assert CACHE_TTL_SECONDS == 24 * 60 * 60
