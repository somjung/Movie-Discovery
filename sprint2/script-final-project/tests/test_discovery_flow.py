"""End-to-end logic tests: search, discovery filters, builder, export."""

import csv

import pytest

from fakes import FakeTmdbClient
from src.discovery import DiscoveryService
from src.exporter import LIST_COLUMNS, ExportError, Exporter
from src.movie_store import MovieStore
from src.sample_data import SAMPLE_MOVIES
from src.tmdb_client import TmdbError
from src.watchlist import WatchlistBuilder

SEED = 27205


@pytest.fixture()
def store(tmp_path):
    db = MovieStore(str(tmp_path / "s2.db"))
    yield db
    db.close()


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


# ---------- Sprint 2: search, sorts, add-by-id, favorites, exports ----------


def test_search_caps_at_ten_and_logs_total(store):
    class ManyHits:
        def search_movies(self, query, page=1):
            return [{"id": i, "title": f"T{i}"} for i in range(1, 15)]

    results = DiscoveryService(ManyHits(), store).search("anything")
    assert len(results) == 10
    assert results[0]["title"] == "T1"
    rows = store.get_recent_searches(1)
    assert rows[0]["query"] == "anything"
    assert rows[0]["result_count"] == 14  # total, not just the 10 shown


def test_search_logs_the_query(store):
    client = FakeTmdbClient()
    results = build_service(store, client).search("alpha")
    assert [movie["title"] for movie in results] == ["Alpha Signal"]
    assert client.search_calls == ["alpha"]
    assert store.get_recent_searches(1)[0]["result_count"] == 1


def test_sort_votes_uses_vote_count_first(store):
    ids = [movie["id"] for movie in
           build_service(store).find_similar(SEED, sort="votes")]
    assert ids == [103, 101, 105, 102, 104]


def test_sort_year_puts_unknown_dates_last(store):
    ids = [movie["id"] for movie in
           build_service(store).find_similar(SEED, sort="year")]
    assert ids == [105, 102, 101, 103, 104]


def test_sort_popularity_descending(store):
    ids = [movie["id"] for movie in
           build_service(store).find_similar(SEED, sort="popularity")]
    assert ids == [103, 101, 105, 102, 104]  # 55, 40, 30, 22, 5


def test_unknown_sort_option_raises(store):
    with pytest.raises(ValueError, match="unknown sort"):
        build_service(store).find_similar(SEED, sort="imdb")


def test_only_kept_movies_are_saved_and_linked(store):
    results = build_service(store).find_similar(SEED, min_rating=8.0)
    assert sorted(movie["id"] for movie in results) == [103, 105]
    links = store.get_similar_links(SEED)
    assert [link["target_id"] for link in links] == [103, 105]  # score DESC
    assert store.get_movie(103) is not None
    assert store.get_movie(101) is None  # filtered out -> not stored


def test_ensure_movie_fetches_once_then_uses_store(store):
    client = FakeTmdbClient()
    builder = WatchlistBuilder(store, client)
    first = builder.ensure_movie(101)
    second = builder.ensure_movie(101)
    assert first["title"] == "Alpha Signal"
    assert second["title"] == "Alpha Signal"
    assert client.detail_calls == [101]


def test_add_returns_true_then_false(store):
    client = FakeTmdbClient()
    builder = WatchlistBuilder(store, client)
    assert builder.add(101) is True
    assert builder.add(101) is False
    assert store.is_in_watchlist(101) is True
    assert client.detail_calls == [101]


def test_add_favorite_refreshes_note(store):
    builder = WatchlistBuilder(store, FakeTmdbClient())
    assert builder.add_favorite(102, note="first") is True
    assert builder.add_favorite(102, note="second") is False
    rows = store.get_favorites()
    assert rows[0]["note"] == "second"


def test_ensure_movie_without_client_raises(store):
    builder = WatchlistBuilder(store)
    with pytest.raises(ValueError, match="no TMDB client"):
        builder.ensure_movie(101)


def test_ensure_movie_propagates_404(store):
    builder = WatchlistBuilder(store, FakeTmdbClient())
    with pytest.raises(TmdbError, match="404"):
        builder.ensure_movie(999)


def test_export_favorites_roundtrip(store, tmp_path):
    for entry in SAMPLE_MOVIES[:2]:
        store.add_movie(entry)
        store.add_favorite(entry["id"])
    out = tmp_path / "favorites.csv"
    assert Exporter.export_favorites(store, str(out)) == 2
    with open(out, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert list(rows[0].keys()) == list(LIST_COLUMNS)
    assert {row["title"] for row in rows} == {"Alpha Signal",
                                              "Bravo Horizon"}


def test_export_keeps_tricky_titles_intact(store, tmp_path):
    tricky = {"id": 900, "title": 'Comma, "quoting" & ไทย',
              "release_date": "2024-01-01", "vote_average": 7.0,
              "vote_count": 10, "popularity": 1.0}
    store.add_movie(tricky)
    store.add_to_watchlist(900, note='note, with "quotes"')
    out = tmp_path / "tricky.csv"
    Exporter.export_watchlist(store, str(out))
    with open(out, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["title"] == tricky["title"]
    assert rows[0]["note"] == 'note, with "quotes"'


def test_export_creates_nested_folders(store, tmp_path):
    store.add_movie(dict(SAMPLE_MOVIES[0]))
    store.add_to_watchlist(101)
    out = tmp_path / "deep" / "nested" / "watchlist.csv"
    assert Exporter.export_watchlist(store, str(out)) == 1
    assert out.exists()


def test_export_empty_list_writes_header_only(store, tmp_path):
    out = tmp_path / "empty.csv"
    assert Exporter.export_watchlist(store, str(out)) == 0
    text = out.read_text(encoding="utf-8")
    assert text.strip() == ",".join(LIST_COLUMNS)


def test_export_error_names_the_path(tmp_path):
    store = MovieStore(":memory:")
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file")
    with pytest.raises(ExportError, match="blocker"):
        Exporter.export_watchlist(store, str(blocker / "out.csv"))
    store.close()
