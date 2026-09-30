"""Test doubles shared by the test-suite."""

from src.sample_data import SAMPLE_MOVIES
from src.tmdb_client import TmdbError


class FakeTmdbClient:
    """Offline stand-in for TmdbClient with canned responses.

    By default the similar list and the recommendation list overlap on
    movie 103, which exercises the dedupe logic.
    """

    def __init__(self, similar=None, recommendations=None):
        self._similar = list(
            similar if similar is not None else SAMPLE_MOVIES[:3]
        )
        self._recommendations = list(
            recommendations if recommendations is not None else SAMPLE_MOVIES[2:]
        )
        # Call counters so tests can prove when the network was avoided.
        self.search_calls = []
        self.detail_calls = []

    def get_similar(self, tmdb_id, page=1):
        return list(self._similar)

    def get_recommendations(self, tmdb_id, page=1):
        return list(self._recommendations)

    def search_movies(self, query, page=1):
        """Titles containing ``query`` (case-insensitive), like TMDB would."""
        self.search_calls.append(query)
        needle = query.lower()
        return [dict(movie) for movie in SAMPLE_MOVIES
                if needle in movie["title"].lower()]

    def get_movie_details(self, tmdb_id):
        """Details for a sample movie; a 404-style error for unknown ids."""
        self.detail_calls.append(tmdb_id)
        for movie in SAMPLE_MOVIES:
            if movie["id"] == tmdb_id:
                return dict(movie)
        raise TmdbError(
            f"TMDB resource not found (HTTP 404): /movie/{tmdb_id}"
        )


class FakeResponse:
    """Minimal requests.Response stand-in for the client tests."""

    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload
