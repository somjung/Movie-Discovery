"""Watchlist and favorites logic: Top-N building and single-movie adds."""


class WatchlistBuilder:
    """Builds the user's Top-N watchlist and adds movies by id.

    The optional ``client`` lets ``add``/``add_favorite`` fetch a movie
    from TMDB when it is not stored locally yet.
    """

    def __init__(self, store, client=None):
        """Keep the store and an optional TMDB client for fetch-by-id."""
        self.store = store
        self.client = client

    def build(self, candidates, top_n=10):
        """Pick up to ``top_n`` new movies and save them to the watchlist."""
        picked = []
        for movie in candidates:
            if self.store.is_in_watchlist(movie["id"]):
                continue
            picked.append(movie)
            if len(picked) >= top_n:
                break
        for movie in picked:
            self.store.add_to_watchlist(movie["id"])
        return picked

    def ensure_movie(self, movie_id):
        """Return the stored movie, fetching it from TMDB when it is missing."""
        movie = self.store.get_movie(movie_id)
        if movie is not None:
            return movie
        if self.client is None:
            raise ValueError(
                f"movie {movie_id} is not stored and no TMDB client is attached"
            )
        self.store.add_movie(self.client.get_movie_details(movie_id))
        return self.store.get_movie(movie_id)

    def add(self, movie_id, note=None):
        """Add one movie to the watchlist by id (fetching it when needed).

        Returns True when it was newly added, and False when it was
        already on the watchlist.
        """
        self.ensure_movie(movie_id)
        already = self.store.is_in_watchlist(movie_id)
        self.store.add_to_watchlist(movie_id, note)
        return not already

    def add_favorite(self, movie_id, note=None):
        """Add one movie to favorites by id (fetching it when needed).

        Returns True when it was newly added, and False when it was
        already in favorites.
        """
        self.ensure_movie(movie_id)
        already = self.store.is_in_favorites(movie_id)
        self.store.add_favorite(movie_id, note)
        return not already
