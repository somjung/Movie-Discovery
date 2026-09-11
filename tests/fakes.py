"""Test doubles shared by the test-suite."""

from src.sample_data import SAMPLE_MOVIES


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

    def get_similar(self, tmdb_id, page=1):
        return list(self._similar)

    def get_recommendations(self, tmdb_id, page=1):
        return list(self._recommendations)


class FakeResponse:
    """Minimal requests.Response stand-in for the client tests."""

    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload
