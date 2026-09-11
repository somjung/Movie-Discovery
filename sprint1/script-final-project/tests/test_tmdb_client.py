"""Unit tests for the TMDB client (network calls are mocked)."""

from unittest.mock import Mock

import pytest
import requests

from fakes import FakeResponse
from src.tmdb_client import TmdbClient, TmdbError

SEARCH_PAYLOAD = {"results": [{"id": 1, "title": "Inception"},
                              {"id": 2, "title": "Interstellar"}]}


def make_client(session):
    return TmdbClient(api_key="test-key", base_url="https://api.test/3",
                      session=session)


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
