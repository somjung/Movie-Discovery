"""Unit tests for the SQLite persistence layer."""

import pytest

from src.movie_store import MovieStore


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
