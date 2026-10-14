"""TMDB API client: read-only GET access with explicit error handling and an
optional SQLite response cache.
"""

import json
from urllib.parse import urlencode

import requests

from .config import TMDB_BASE_URL, DEFAULT_LANGUAGE, DEFAULT_TIMEOUT, get_api_key
from .movie_store import CACHE_TTL_SECONDS


class TmdbError(Exception):
    """Raised when a TMDB request cannot be completed."""


class TmdbClient:
    """Minimal TMDB REST client (only the endpoints this project needs).

    Pass a ``store`` to enable response caching in its ``api_cache`` table:
    a request that is still fresh is served from SQLite without any network
    call; everything else is fetched and then stored for next time.
    """

    def __init__(self, api_key=None, base_url=TMDB_BASE_URL,
                 timeout=DEFAULT_TIMEOUT, session=None, store=None,
                 cache_ttl=CACHE_TTL_SECONDS):
        """Build a client; ``store=None`` disables the response cache."""
        self.api_key = api_key if api_key is not None else get_api_key()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()
        self.store = store
        self.cache_ttl = cache_ttl
        # Counters the CLI and tests can read to show the cache working.
        self.cache_hits = 0
        self.cache_misses = 0

    def _cache_key(self, path, query):
        """Deterministic key: the path plus every parameter except the API key."""
        public = sorted((key, value) for key, value in query.items()
                        if key != "api_key")
        return f"{path}?{urlencode(public)}"

    def _read_cache(self, cache_key):
        """Fresh cached body as a dict, or None (absent, expired, or corrupt)."""
        if self.store is None:
            return None
        cached = self.store.get_cached(cache_key, self.cache_ttl)
        if cached is None:
            return None
        try:
            return json.loads(cached)
        except ValueError:
            return None  # corrupt entry: ignore it and refetch from the API

    def _write_cache(self, cache_key, payload):
        """Store a fresh response body for future reads (no-op without a store)."""
        if self.store is not None:
            self.store.save_cached(cache_key, json.dumps(payload))

    def _get(self, path, params=None):
        """GET ``path`` and return the decoded JSON body.

        Served from the cache when fresh; otherwise fetched from the network
        and stored. Every failure mode raises TmdbError with a readable
        message: network problems, auth failures, missing resources, rate
        limits, unexpected statuses, and invalid JSON.
        """
        query = {"api_key": self.api_key, "language": DEFAULT_LANGUAGE}
        if params:
            query.update(params)
        cache_key = self._cache_key(path, query)

        cached = self._read_cache(cache_key)
        if cached is not None:
            self.cache_hits += 1
            return cached
        if self.store is not None:
            self.cache_misses += 1

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
            payload = response.json()
        except ValueError as exc:
            raise TmdbError(f"TMDB returned invalid JSON for {path}") from exc
        self._write_cache(cache_key, payload)
        return payload

    def search_movies(self, query, page=1):
        """Search movies by title. Returns a list of movie dicts."""
        data = self._get("/search/movie", {"query": query, "page": page})
        return data.get("results", [])

    def get_movie_details(self, tmdb_id):
        """Full details for one movie id (used when adding it by id)."""
        return self._get(f"/movie/{tmdb_id}")

    def get_similar(self, tmdb_id, page=1):
        """Movies similar to a given movie id."""
        data = self._get(f"/movie/{tmdb_id}/similar", {"page": page})
        return data.get("results", [])

    def get_recommendations(self, tmdb_id, page=1):
        """TMDB's recommendations for a given movie id."""
        data = self._get(f"/movie/{tmdb_id}/recommendations", {"page": page})
        return data.get("results", [])
