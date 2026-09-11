"""Configuration constants and API-key lookup for the project."""

import os

TMDB_BASE_URL = "https://api.themoviedb.org/3"
DEFAULT_LANGUAGE = "en-US"
DEFAULT_TIMEOUT = 10


def get_api_key():
    """Return the TMDB API key from the environment.

    Raises RuntimeError with a helpful message when the key is missing.
    """
    api_key = os.environ.get("TMDB_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "TMDB_API_KEY is not set. Create a free key at "
            "https://developer.themoviedb.org/ and export it, e.g. "
            "set TMDB_API_KEY=your_key_here"
        )
    return api_key
