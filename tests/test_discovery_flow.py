"""End-to-end logic tests: discovery filters, watchlist builder, CSV export."""

import csv

from fakes import FakeTmdbClient
from src.discovery import DiscoveryService
from src.exporter import Exporter
from src.movie_store import MovieStore
from src.watchlist import WatchlistBuilder

SEED = 27205


def build_service(store, client=None):
    return DiscoveryService(client or FakeTmdbClient(), store)


def test_dedupe_merges_similar_and_recommendations(tmp_path):
    store = MovieStore(str(tmp_path / "a.db"))
    results = build_service(store).find_similar(SEED, limit=10)
    ids = [movie["id"] for movie in results]
    assert len(ids) == len(set(ids))  # movie 103 is in both source lists
    assert 103 in ids
    store.close()


def test_min_rating_filter(tmp_path):
    store = MovieStore(str(tmp_path / "b.db"))
    results = build_service(store).find_similar(SEED, min_rating=8.0)
    assert sorted(movie["id"] for movie in results) == [103, 105]
    store.close()


def test_year_range_excludes_unknown_dates(tmp_path):
    store = MovieStore(str(tmp_path / "c.db"))
    results = build_service(store).find_similar(SEED, year_from=2010,
                                                year_to=2020)
    assert sorted(movie["id"] for movie in results) == [101, 102]  # 104: no date
    store.close()


def test_ranking_prefers_rating_then_votes(tmp_path):
    store = MovieStore(str(tmp_path / "d.db"))
    results = build_service(store).find_similar(SEED)
    assert results[0]["id"] == 103  # 8.4 beats everything else
    store.close()


def test_limit_is_applied(tmp_path):
    store = MovieStore(str(tmp_path / "e.db"))
    results = build_service(store).find_similar(SEED, limit=2)
    assert len(results) == 2
    store.close()


def test_watchlist_builder_skips_saved_movies(tmp_path):
    store = MovieStore(str(tmp_path / "f.db"))
    results = build_service(store).find_similar(SEED)
    builder = WatchlistBuilder(store)
    first = builder.build(results, top_n=2)
    assert len(first) == 2
    again = builder.build(results, top_n=2)
    assert [movie["id"] for movie in again] == \
        [movie["id"] for movie in results[2:4]]
    store.close()


def test_csv_export_roundtrip(tmp_path):
    store = MovieStore(str(tmp_path / "g.db"))
    results = build_service(store).find_similar(SEED)
    WatchlistBuilder(store).build(results, top_n=3)
    out = tmp_path / "watchlist.csv"
    Exporter.export_watchlist(store, str(out))
    with open(out, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    assert rows[0]["title"]
    store.close()
