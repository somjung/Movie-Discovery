"""Discovery logic: fetch candidates for a seed movie, filter, dedupe, rank."""


class DiscoveryService:
    """Turns a seed movie id into a ranked candidate list.

    The API only supplies raw similar/recommended movies; which of them
    survive the filters and in which order is decided here (project logic).
    """

    def __init__(self, client, store):
        self.client = client
        self.store = store

    def find_similar(self, seed_id, min_rating=0.0, min_votes=0,
                     year_from=None, year_to=None, limit=10):
        """Return the top ``limit`` candidates for the seed movie."""
        candidates = {}
        for fetch in (self.client.get_similar, self.client.get_recommendations):
            for movie in fetch(seed_id):
                candidates.setdefault(movie["id"], movie)

        kept = [
            movie for movie in candidates.values()
            if self._passes_filters(movie, min_rating, min_votes,
                                    year_from, year_to)
        ]
        kept.sort(
            key=lambda movie: (movie.get("vote_average") or 0,
                               movie.get("vote_count") or 0),
            reverse=True,
        )
        kept = kept[:limit]

        for movie in kept:
            self.store.add_movie(movie)
            self.store.add_similar_link(seed_id, movie["id"],
                                        movie.get("vote_average"))
        return kept

    @staticmethod
    def release_year(movie):
        """Release year as int, or 0 when the date is unknown/invalid."""
        date = (movie.get("release_date") or "")[:4]
        return int(date) if date.isdigit() else 0

    @classmethod
    def _passes_filters(cls, movie, min_rating, min_votes, year_from, year_to):
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
