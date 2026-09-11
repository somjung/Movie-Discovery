"""Top-N watchlist builder: pick candidates, skip the ones already saved."""


class WatchlistBuilder:
    """Builds the user's Top-N watchlist from ranked candidates."""

    def __init__(self, store):
        self.store = store

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
