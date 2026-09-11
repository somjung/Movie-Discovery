"""Built-in sample dataset used by the Sprint 1 CLI and the test-suite.

The TMDB-backed data layer arrives in Sprint 2; until then the CLI is
demonstrated safely offline with these five movies.
"""

SAMPLE_MOVIES = [
    {"id": 101, "title": "Alpha Signal", "release_date": "2010-05-01",
     "vote_average": 7.8, "vote_count": 1200, "popularity": 40.0},
    {"id": 102, "title": "Bravo Horizon", "release_date": "2014-09-12",
     "vote_average": 6.1, "vote_count": 300, "popularity": 22.0},
    {"id": 103, "title": "Cobalt Night", "release_date": "1999-01-20",
     "vote_average": 8.4, "vote_count": 2100, "popularity": 55.0},
    {"id": 104, "title": "Delta Echo", "release_date": "",
     "vote_average": 5.0, "vote_count": 50, "popularity": 5.0},
    {"id": 105, "title": "Emerald Run", "release_date": "2021-11-05",
     "vote_average": 8.0, "vote_count": 900, "popularity": 30.0},
]
