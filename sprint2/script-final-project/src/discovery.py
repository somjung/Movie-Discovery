"""Discovery logic: search, filter, sort, dedupe and rank movie candidates."""

SORT_OPTIONS = ("rating", "votes", "year", "popularity")


class DiscoveryService:
    """Turns user queries and seed ids into ranked candidate lists.

    The API only supplies raw search/similar/recommended movies; which of
    them survive the filters and in which order is decided here (project
    logic), and everything shown to the user is kept in the local store.
    """

    def __init__(self, client, store):
        """Keep the API client and the local store the service writes to."""
        self.client = client
        self.store = store

    def search(self, query, limit=10):
        """Search TMDB for ``query``, log it in ``searches``, return top hits."""
        results = self.client.search_movies(query)
        self.store.record_search(query, len(results))
        return results[:limit]

    def find_similar(self, seed_id, min_rating=0.0, min_votes=0,
                     year_from=None, year_to=None, limit=10, sort="rating"):
        """Return the top ``limit`` candidates for the seed movie.

        Candidates come from the similar + recommended endpoints (merged,
        with duplicates removed), then are filtered, sorted by ``sort``
        and cut down to ``limit`` before being saved to the store.
        """
        candidates = {}
        for fetch in (self.client.get_similar, self.client.get_recommendations):
            for movie in fetch(seed_id):
                candidates.setdefault(movie["id"], movie)

        kept = [
            movie for movie in candidates.values()
            if self._passes_filters(movie, min_rating, min_votes,
                                    year_from, year_to)
        ]
        kept.sort(key=self._sort_key(sort), reverse=True)
        kept = kept[:limit]

        for movie in kept:
            self.store.add_movie(movie)
            self.store.add_similar_link(seed_id, movie["id"],
                                        movie.get("vote_average"))
        return kept

    @classmethod
    def _sort_key(cls, sort):
        """Pick the (primary, secondary) sort key; reject unknown names."""
        if sort not in SORT_OPTIONS:
            raise ValueError(f"unknown sort option: {sort!r}")
        keys = {
            "rating": lambda movie: (movie.get("vote_average") or 0,
                                     movie.get("vote_count") or 0),
            "votes": lambda movie: (movie.get("vote_count") or 0,
                                    movie.get("vote_average") or 0),
            "year": lambda movie: (cls.release_year(movie),
                                   movie.get("vote_average") or 0),
            "popularity": lambda movie: (movie.get("popularity") or 0,
                                         movie.get("vote_average") or 0),
        }
        return keys[sort]

    @staticmethod
    def release_year(movie):
        """Release year as int, or 0 when the date is unknown/invalid."""
        date = (movie.get("release_date") or "")[:4]
        return int(date) if date.isdigit() else 0

    @classmethod
    def _passes_filters(cls, movie, min_rating, min_votes, year_from, year_to):
        """True when the movie satisfies every active filter."""
        if (movie.get("vote_average") or 0) < min_rating:
            return False
        if (movie.get("vote_count") or 0) < min_votes:
            return False
        year = cls.release_year(movie)
        if year == 0 and (year_from or year_to):
            return False  # an unknown date cannot be placed inside a range
        if year_from and year < year_from:
            return False
        if year_to and year > year_to:
            return False
        return True
