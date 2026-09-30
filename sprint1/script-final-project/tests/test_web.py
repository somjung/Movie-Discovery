"""Web-layer tests (Sprint 3): every route, offline, no key, no network.

Uses the Flask test client with the shared fakes and an in-memory store.
Media tests write a small dummy video file into the temp data dir, so
the real movie file is never needed and CI stays keyless.
"""

import pytest

from fakes import FakeTmdbClient
from src.cli import CLI
from src.exporter import LIST_COLUMNS
from src.movie_store import MovieStore
from src.sample_data import SAMPLE_MOVIES
from src.tmdb_client import TmdbError
from src.watchlist import WatchlistBuilder
from web import create_app

VIDEO_NAME = "night_of_the_living_dead.mp4"
VIDEO_PAYLOAD = bytes(range(256)) * 4


def write_video(tmp_path, name=VIDEO_NAME, payload=VIDEO_PAYLOAD):
    """Place a dummy video file in the temp data dir and return its path."""
    videos = tmp_path / "videos"
    videos.mkdir(exist_ok=True)
    path = videos / name
    path.write_bytes(payload)
    return path


class PlayableFake(FakeTmdbClient):
    """Fake client that knows TMDB id 10331 (the local demo movie)."""

    DETAIL = {
        "id": 10331,
        "title": "Night of the Living Dead",
        "release_date": "1968-10-01",
        "vote_average": 7.6,
        "vote_count": 1500,
        "popularity": 30.0,
        "overview": "A group of people hide from zombies in a farmhouse.",
        "poster_path": None,
        "backdrop_path": None,
    }

    def get_movie_details(self, tmdb_id):
        if tmdb_id == 10331:
            self.detail_calls.append(tmdb_id)
            return dict(self.DETAIL)
        return super().get_movie_details(tmdb_id)

    def get_similar(self, tmdb_id, page=1):
        if tmdb_id == 10331:
            return [dict(self.DETAIL)]
        return super().get_similar(tmdb_id, page)

    def get_recommendations(self, tmdb_id, page=1):
        if tmdb_id == 10331:
            return []
        return super().get_recommendations(tmdb_id, page)


class FlakyFake(FakeTmdbClient):
    """Fake client that raises TmdbError on the chosen calls."""

    def __init__(self, fail_on=(), message="HTTP 503 service unavailable"):
        super().__init__()
        self.fail_on = set(fail_on)
        self.message = message

    def search_movies(self, query, page=1):
        if "search" in self.fail_on:
            raise TmdbError(self.message)
        return super().search_movies(query, page)

    def get_movie_details(self, tmdb_id):
        if "detail" in self.fail_on:
            raise TmdbError(self.message)
        return super().get_movie_details(tmdb_id)

    def get_similar(self, tmdb_id, page=1):
        if "similar" in self.fail_on:
            raise TmdbError(self.message)
        return super().get_similar(tmdb_id, page)

    def get_recommendations(self, tmdb_id, page=1):
        if "similar" in self.fail_on:
            raise TmdbError(self.message)
        return super().get_recommendations(tmdb_id, page)


@pytest.fixture()
def store():
    """Fresh in-memory store for one test."""
    instance = MovieStore(":memory:")
    yield instance
    instance.close()


def make_client(tmp_path, store, client):
    """App with ``client`` (None = keyless mode) and a temp data dir."""
    app = create_app(client=client, store=store, data_dir=str(tmp_path))
    return app.test_client()


class TestHome:
    def test_home_opens_with_key(self, tmp_path, store):
        resp = make_client(tmp_path, store, FakeTmdbClient()).get("/")
        assert resp.status_code == 200
        assert "Movie Discovery" in resp.get_data(as_text=True)

    def test_home_shows_key_banner_when_missing(self, tmp_path, store):
        resp = make_client(tmp_path, store, None).get("/")
        assert resp.status_code == 200
        assert "ยังไม่ได้ตั้งค่าคีย์" in resp.get_data(as_text=True)


class TestSearch:
    def test_results_page(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        needle = SAMPLE_MOVIES[0]["title"]
        resp = client.get(f"/search?q={needle}")
        assert resp.status_code == 200
        assert needle in resp.get_data(as_text=True)

    def test_empty_query_gets_hint(self, tmp_path, store):
        resp = make_client(tmp_path, store, FakeTmdbClient()).get("/search?q=")
        assert "กรุณาพิมพ์คำค้นก่อนกดค้นหา" in resp.get_data(as_text=True)

    def test_whitespace_query_gets_hint(self, tmp_path, store):
        resp = make_client(tmp_path, store, FakeTmdbClient()).get(
            "/search?q=%20%20%20")
        assert "กรุณาพิมพ์คำค้นก่อนกดค้นหา" in resp.get_data(as_text=True)

    def test_keyless_guidance(self, tmp_path, store):
        resp = make_client(tmp_path, store, None).get("/search?q=test")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "TMDB_API_KEY" in html

    def test_no_results_message(self, tmp_path, store):
        resp = make_client(tmp_path, store, FakeTmdbClient()).get(
            "/search?q=zzz-nothing")
        assert "ไม่พบภาพยนตร์ที่ตรงกับ" in resp.get_data(as_text=True)

    def test_long_query_truncated(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        resp = client.get("/search?q=" + "a" * 300)
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "ยาวเกิน 120" in html

    def test_emoji_query_does_not_crash(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        resp = client.get("/search?q=%F0%9F%98%80%F0%9F%91%8D")
        assert resp.status_code == 200

    def test_script_query_is_escaped(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        resp = client.get("/search?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E")
        html = resp.get_data(as_text=True)
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html

    @pytest.mark.parametrize("message", [
        "HTTP 401 unauthorized",
        "HTTP 429 too many requests",
        "HTTP 503 service unavailable",
    ])
    def test_tmdb_errors_use_cli_wording(self, tmp_path, message):
        app = create_app(client=FlakyFake(fail_on=("search",),
                                          message=message),
                         store=MovieStore(":memory:"),
                         data_dir=str(tmp_path))
        resp = app.test_client().get("/search?q=x")
        assert resp.status_code == 502
        expected = CLI.describe_tmdb_error(TmdbError(message))
        assert expected in resp.get_data(as_text=True)


class TestMovieDetail:
    def test_detail_page_with_buttons(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        movie = SAMPLE_MOVIES[0]
        resp = client.get(f"/movie/{movie['id']}")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert movie["title"] in html
        assert f"/watchlist/add/{movie['id']}" in html
        assert f"/favorites/add/{movie['id']}" in html

    def test_bad_filter_values_fall_back_with_notes(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        mid = SAMPLE_MOVIES[0]["id"]
        resp = client.get(
            f"/movie/{mid}?min_rating=abc&limit=999"
            "&sort=nope&year_from=2000&year_to=1990")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "ไม่ใช่ตัวเลข" in html
        assert "อยู่นอกช่วงที่รองรับ" in html
        assert "ไม่รู้จักวิธีเรียง" in html
        assert "ช่วงปีสลับกัน" in html

    def test_unknown_movie_id_polite_404(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        resp = client.get("/movie/424242")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 404
        assert "ไม่พบภาพยนตร์" in html

    @pytest.mark.parametrize("bad_path", ["/movie/abc", "/movie/-5"])
    def test_non_matching_ids_404(self, tmp_path, store, bad_path):
        client = make_client(tmp_path, store, FakeTmdbClient())
        assert client.get(bad_path).status_code == 404

    def test_similar_failure_shows_inline(self, tmp_path, store):
        app = create_app(client=FlakyFake(fail_on=("similar",),
                                          message="HTTP 503 sim failed"),
                         store=store, data_dir=str(tmp_path))
        resp = app.test_client().get(f"/movie/{SAMPLE_MOVIES[0]['id']}")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert SAMPLE_MOVIES[0]["title"] in html
        expected = CLI.describe_tmdb_error(TmdbError("HTTP 503 sim failed"))
        assert expected in html

    def test_detail_down_returns_502(self, tmp_path, store):
        app = create_app(client=FlakyFake(fail_on=("detail",),
                                          message="HTTP 503 detail down"),
                         store=store, data_dir=str(tmp_path))
        resp = app.test_client().get(f"/movie/{SAMPLE_MOVIES[0]['id']}")
        assert resp.status_code == 502

    def test_offline_mode_saved_movie(self, tmp_path, store):
        store.add_movie(dict(SAMPLE_MOVIES[0]))
        resp = make_client(tmp_path, store, None).get(
            f"/movie/{SAMPLE_MOVIES[0]['id']}")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "โหมดไม่มีคีย์" in html

    def test_offline_mode_unsaved_movie_404(self, tmp_path, store):
        resp = make_client(tmp_path, store, None).get("/movie/424242")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 404
        assert "ไม่มีข้อมูลภาพยนตร์เรื่องนี้ในเครื่อง" in html


class TestListActions:
    def test_watchlist_add_exists_remove_missing(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        mid = SAMPLE_MOVIES[1]["id"]

        def text(resp):
            return resp.get_data(as_text=True)

        resp = client.post(f"/watchlist/add/{mid}", follow_redirects=True)
        assert "เพิ่มเข้าสู่รายการรับชมแล้ว" in text(resp)
        resp = client.post(f"/watchlist/add/{mid}", follow_redirects=True)
        assert "อยู่ในรายการรับชมอยู่แล้ว" in text(resp)
        resp = client.post(f"/watchlist/remove/{mid}", follow_redirects=True)
        assert "ลบออกจากรายการรับชมแล้ว" in text(resp)
        resp = client.post(f"/watchlist/remove/{mid}", follow_redirects=True)
        assert "ไม่พบเรื่องนี้ในรายการรับชม" in text(resp)

    def test_favorites_add_and_duplicate(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        mid = SAMPLE_MOVIES[0]["id"]
        resp = client.post(f"/favorites/add/{mid}", follow_redirects=True)
        assert "เพิ่มเข้าสู่รายการโปรดแล้ว" in resp.get_data(as_text=True)
        resp = client.post(f"/favorites/add/{mid}", follow_redirects=True)
        assert "อยู่ในรายการโปรดอยู่แล้ว" in resp.get_data(as_text=True)

    @pytest.mark.parametrize("evil", [
        "//evil.example/x",
        "/\\evil.example/x",
        "http://evil.example/x",
        "",
    ])
    def test_next_is_restricted_to_local_paths(self, tmp_path, store, evil):
        client = make_client(tmp_path, store, FakeTmdbClient())
        mid = SAMPLE_MOVIES[0]["id"]
        resp = client.post(f"/watchlist/add/{mid}", data={"next": evil})
        assert resp.status_code == 303
        assert resp.headers["Location"].startswith(f"/movie/{mid}")

    def test_clear_watchlist_flow(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        mid = SAMPLE_MOVIES[1]["id"]
        client.post(f"/watchlist/add/{mid}")
        resp = client.post("/watchlist/clear", follow_redirects=True)
        html = resp.get_data(as_text=True)
        assert "ล้างรายการรับชมเรียบร้อยแล้ว (1 เรื่อง)" in html
        assert "ยังไม่มีรายการ" in html

    def test_keyless_add_without_local_data(self, tmp_path, store):
        client = make_client(tmp_path, store, None)
        resp = client.post("/watchlist/add/424242")
        assert resp.status_code == 303
        assert "error=nodata" in resp.headers["Location"]


class TestListPages:
    def test_watchlist_page_shows_rows(self, tmp_path, store):
        WatchlistBuilder(store, FakeTmdbClient()).add(SAMPLE_MOVIES[0]["id"])
        resp = make_client(tmp_path, store, FakeTmdbClient()).get("/watchlist")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "รายการรับชม (1)" in html
        assert SAMPLE_MOVIES[0]["title"] in html

    def test_empty_list_notice(self, tmp_path, store):
        resp = make_client(tmp_path, store, FakeTmdbClient()).get("/favorites")
        assert "ยังไม่มีรายการ" in resp.get_data(as_text=True)

    def test_cross_list_star_only_when_shared(self, tmp_path, store):
        shared = SAMPLE_MOVIES[0]["id"]
        only_watch = SAMPLE_MOVIES[1]["id"]
        builder = WatchlistBuilder(store, FakeTmdbClient())
        builder.add(shared)
        builder.add(only_watch)
        builder.add_favorite(shared)
        client = make_client(tmp_path, store, FakeTmdbClient())
        html_watch = client.get("/watchlist").get_data(as_text=True)
        html_fav = client.get("/favorites").get_data(as_text=True)
        assert html_watch.count('class="star"') == 1
        assert html_fav.count('class="star"') == 1

    def test_history_lists_searches(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        needle = SAMPLE_MOVIES[0]["title"]
        client.get(f"/search?q={needle}")
        resp = client.get("/history")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert needle in html

    def test_history_bad_limit_falls_back(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        assert client.get("/history?limit=abc").status_code == 200
        assert client.get("/history?limit=999").status_code == 200

    def test_export_watchlist_csv_content(self, tmp_path, store):
        WatchlistBuilder(store, FakeTmdbClient()).add(SAMPLE_MOVIES[0]["id"])
        client = make_client(tmp_path, store, FakeTmdbClient())
        resp = client.get("/export/watchlist")
        assert resp.status_code == 200
        assert "attachment" in resp.headers["Content-Disposition"]
        body = resp.get_data().decode("utf-8-sig")
        lines = body.splitlines()
        assert lines[0] == ",".join(LIST_COLUMNS)
        assert str(SAMPLE_MOVIES[0]["id"]) in lines[1]

    def test_export_empty_is_header_only(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        resp = client.get("/export/favorites")
        body = resp.get_data().decode("utf-8-sig")
        assert resp.status_code == 200
        assert body.splitlines() == [",".join(LIST_COLUMNS)]

    def test_export_bad_kind_404(self, tmp_path, store):
        client = make_client(tmp_path, store, FakeTmdbClient())
        assert client.get("/export/whatever").status_code == 404


class TestPlayer:
    def test_player_without_file_shows_guidance(self, tmp_path, store):
        resp = make_client(tmp_path, store, PlayableFake()).get("/play/10331")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "ไฟล์หนังยังไม่มีในเครื่อง" in html
        assert "fetch_demo_video.py" in html

    def test_player_with_file_renders_video(self, tmp_path, store):
        write_video(tmp_path)
        resp = make_client(tmp_path, store, PlayableFake()).get("/play/10331")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert f'src="/media/{VIDEO_NAME}"' in html
        assert "Night of the Living Dead (1968)" in html
        assert "archive.org" in html

    def test_unknown_movie_gets_notice(self, tmp_path, store):
        resp = make_client(tmp_path, store, PlayableFake()).get("/play/999")
        assert "ยังไม่มีไฟล์สำหรับเรื่องนี้" in resp.get_data(as_text=True)

    def test_detail_page_shows_play_button_and_badge(self, tmp_path, store):
        write_video(tmp_path)
        resp = make_client(tmp_path, store, PlayableFake()).get("/movie/10331")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "▶ เล่นหนัง" in html
        assert 'class="play-badge"' in html

    def test_media_serves_full_file(self, tmp_path, store):
        write_video(tmp_path)
        resp = make_client(tmp_path, store, PlayableFake()).get(
            f"/media/{VIDEO_NAME}")
        assert resp.status_code == 200
        assert resp.headers["Content-Type"].startswith("video/mp4")
        assert resp.get_data() == VIDEO_PAYLOAD
        resp.close()

    def test_media_supports_range(self, tmp_path, store):
        write_video(tmp_path)
        resp = make_client(tmp_path, store, PlayableFake()).get(
            f"/media/{VIDEO_NAME}", headers={"Range": "bytes=0-9"})
        assert resp.status_code == 206
        assert resp.get_data() == VIDEO_PAYLOAD[:10]
        header = resp.headers["Content-Range"]
        assert f"bytes 0-9/{len(VIDEO_PAYLOAD)}" in header
        resp.close()

    def test_media_unknown_name_404(self, tmp_path, store):
        resp = make_client(tmp_path, store, PlayableFake()).get(
            "/media/nope.mp4")
        assert resp.status_code == 404

    def test_media_traversal_blocked(self, tmp_path, store):
        client = make_client(tmp_path, store, PlayableFake())
        assert client.get("/media/..%2F..%2Fapp.py").status_code == 404

    def test_fallback_file_changes_label(self, tmp_path, store):
        write_video(tmp_path, name="big_buck_bunny.mp4", payload=b"bb")
        resp = make_client(tmp_path, store, PlayableFake()).get("/play/10331")
        html = resp.get_data(as_text=True)
        assert 'src="/media/big_buck_bunny.mp4"' in html
        assert "Big Buck Bunny (2008)" in html


class TestErrorPages:
    def test_unknown_url_404(self, tmp_path, store):
        resp = make_client(tmp_path, store, FakeTmdbClient()).get("/no-such")
        assert resp.status_code == 404
        assert "ไม่พบหน้าที่ต้องการ" in resp.get_data(as_text=True)

    def test_corrupt_database_shows_repair_page(self, tmp_path):
        bad_db = tmp_path / "movies.db"
        bad_db.write_bytes(b"this is definitely not a sqlite database " * 10)
        app = create_app(db_path=str(bad_db), data_dir=str(tmp_path))
        client = app.test_client()
        resp = client.get("/")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 500
        assert "ฐานข้อมูลมีปัญหา" in html
        assert "ย้ายหรือลบ" in html
        assert "movies.db" in html
        assert client.get("/watchlist").status_code == 500
