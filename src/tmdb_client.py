"""TMDB API client: read-only GET access with explicit error handling."""

import requests

from .config import TMDB_BASE_URL, DEFAULT_LANGUAGE, DEFAULT_TIMEOUT, get_api_key


class TmdbError(Exception):
    """Raised when a TMDB request cannot be completed."""


class TmdbClient:
    """Minimal TMDB REST client (only the endpoints this project needs)."""

    def __init__(self, api_key=None, base_url=TMDB_BASE_URL,
                 timeout=DEFAULT_TIMEOUT, session=None):
        self.api_key = api_key if api_key is not None else get_api_key()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()

    def _get(self, path, params=None):
        """GET ``path`` and return the decoded JSON body.

        Every failure mode raises TmdbError with a readable message:
        network problems, auth failures, missing resources, rate limits,
        unexpected statuses, and invalid JSON.
        """
        query = {"api_key": self.api_key, "language": DEFAULT_LANGUAGE}
        if params:
            query.update(params)
        try:
            response = self.session.get(
                f"{self.base_url}{path}", params=query, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise TmdbError(f"request to {path} failed: {exc}") from exc

        if response.status_code == 401:
            raise TmdbError("TMDB rejected the API key (HTTP 401)")
        if response.status_code == 404:
            raise TmdbError(f"TMDB resource not found (HTTP 404): {path}")
        if response.status_code == 429:
            raise TmdbError("TMDB rate limit hit (HTTP 429) - slow down")
        if response.status_code != 200:
            raise TmdbError(
                f"unexpected TMDB status {response.status_code} for {path}"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise TmdbError(f"TMDB returned invalid JSON for {path}") from exc

    def search_movies(self, query, page=1):
        """Search movies by title. Returns a list of movie dicts."""
        data = self._get("/search/movie", {"query": query, "page": page})
        return data.get("results", [])

    def get_similar(self, tmdb_id, page=1):
        """Movies similar to a given movie id."""
        data = self._get(f"/movie/{tmdb_id}/similar", {"page": page})
        return data.get("results", [])

    def get_recommendations(self, tmdb_id, page=1):
        """TMDB's recommendations for a given movie id."""
        data = self._get(f"/movie/{tmdb_id}/recommendations", {"page": page})
        return data.get("results", [])
