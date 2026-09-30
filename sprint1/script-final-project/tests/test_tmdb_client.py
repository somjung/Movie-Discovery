"""Unit tests for the TMDB client (network calls are mocked)."""

import json
from unittest.mock import Mock

import pytest
import requests

from fakes import FakeResponse
from src.movie_store import MovieStore
from src.tmdb_client import TmdbClient, TmdbError

SEARCH_PAYLOAD = {"results": [{"id": 1, "title": "Inception"},
                              {"id": 2, "title": "Interstellar"}]}


def make_client(session):
    return TmdbClient(api_key="test-key", base_url="https://api.test/3",
                      session=session)


def make_cached_client(session, store, api_key="test-key"):
    return TmdbClient(api_key=api_key, base_url="https://api.test/3",
                      session=session, store=store)


def test_search_movies_returns_results():
    session = Mock()
    session.get.return_value = FakeResponse(200, SEARCH_PAYLOAD)
    client = make_client(session)
    results = client.search_movies("inception")
    assert [movie["id"] for movie in results] == [1, 2]


def test_get_sends_api_key_language_and_query():
    session = Mock()
    session.get.return_value = FakeResponse(200, SEARCH_PAYLOAD)
    client = make_client(session)
    client.search_movies("inception")
    args, kwargs = session.get.call_args
    assert args[0] == "https://api.test/3/search/movie"
    assert kwargs["params"]["api_key"] == "test-key"
    assert kwargs["params"]["language"] == "en-US"
    assert kwargs["params"]["query"] == "inception"


def test_auth_error_raises_tmdb_error():
    session = Mock()
    session.get.return_value = FakeResponse(401)
    client = make_client(session)
    with pytest.raises(TmdbError, match="401"):
        client.search_movies("x")


def test_not_found_raises_tmdb_error():
    session = Mock()
    session.get.return_value = FakeResponse(404)
    client = make_client(session)
    with pytest.raises(TmdbError, match="404"):
        client.get_similar(27205)


def test_rate_limit_raises_tmdb_error():
    session = Mock()
    session.get.return_value = FakeResponse(429)
    client = make_client(session)
    with pytest.raises(TmdbError, match="429"):
        client.get_recommendations(27205)


def test_network_failure_raises_tmdb_error():
    session = Mock()
    session.get.side_effect = requests.ConnectionError("boom")
    client = make_client(session)
    with pytest.raises(TmdbError, match="request to"):
        client.search_movies("x")


def test_invalid_json_raises_tmdb_error():
    session = Mock()
    session.get.return_value = FakeResponse(200, ValueError("bad json"))
    client = make_client(session)
    with pytest.raises(TmdbError, match="invalid JSON"):
        client.search_movies("x")


# ---------- Sprint 2: response cache (store-backed) ----------


def test_cache_hit_skips_the_network():
    store = MovieStore(":memory:")
    session = Mock()
    session.get.return_value = FakeResponse(200, SEARCH_PAYLOAD)
    client = make_cached_client(session, store)
    first = client.search_movies("inception")
    second = client.search_movies("inception")
    assert session.get.call_count == 1
    assert second == first
    assert client.cache_misses == 1
    assert client.cache_hits == 1
    store.close()


def test_cache_key_ignores_the_api_key():
    store = MovieStore(":memory:")
    first_session = Mock()
    first_session.get.return_value = FakeResponse(200, SEARCH_PAYLOAD)
    make_cached_client(first_session, store).search_movies("inception")
    second_session = Mock()
    client = make_cached_client(second_session, store, api_key="other-key")
    results = client.search_movies("inception")
    assert second_session.get.call_count == 0
    assert [movie["id"] for movie in results] == [1, 2]
    store.close()


def test_errors_are_not_cached():
    store = MovieStore(":memory:")
    session = Mock()
    session.get.return_value = FakeResponse(401)
    client = make_cached_client(session, store)
    with pytest.raises(TmdbError, match="401"):
        client.search_movies("x")
    count = store.conn.execute("SELECT COUNT(*) FROM api_cache").fetchone()[0]
    assert count == 0
    store.close()


def test_corrupt_cache_entry_is_refetched():
    store = MovieStore(":memory:")
    session = Mock()
    session.get.return_value = FakeResponse(200, SEARCH_PAYLOAD)
    client = make_cached_client(session, store)
    client.search_movies("inception")
    store.conn.execute("UPDATE api_cache SET payload = 'not json'")
    store.conn.commit()
    results = client.search_movies("inception")
    assert session.get.call_count == 2
    assert [movie["id"] for movie in results] == [1, 2]
    payload = store.conn.execute("SELECT payload FROM api_cache").fetchone()[0]
    assert json.loads(payload)["results"][0]["id"] == 1
    store.close()


def test_expired_cache_entry_is_refetched():
    store = MovieStore(":memory:")
    session = Mock()
    session.get.return_value = FakeResponse(200, SEARCH_PAYLOAD)
    client = make_cached_client(session, store)
    client.search_movies("inception")
    store.conn.execute(
        "UPDATE api_cache SET fetched_at = datetime('now', '-2 days')"
    )
    store.conn.commit()
    client.search_movies("inception")
    assert session.get.call_count == 2
    store.close()


def test_client_without_store_does_not_cache():
    session = Mock()
    session.get.return_value = FakeResponse(200, SEARCH_PAYLOAD)
    client = make_client(session)
    client.search_movies("inception")
    client.search_movies("inception")
    assert session.get.call_count == 2
    assert client.cache_hits == 0
    assert client.cache_misses == 0


def test_get_movie_details_is_cached():
    store = MovieStore(":memory:")
    session = Mock()
    session.get.return_value = FakeResponse(
        200, {"id": 27205, "title": "Inception"}
    )
    client = make_cached_client(session, store)
    first = client.get_movie_details(27205)
    second = client.get_movie_details(27205)
    assert session.get.call_count == 1
    assert first == second == {"id": 27205, "title": "Inception"}
    store.close()
