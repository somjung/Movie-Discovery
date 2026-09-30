"""Page routes for the web front-end (Sprint 3).

Implemented so far: the home page, the search results page, the movie
details page (similar movies, filters and list buttons), the two list
pages (cross-list stars, CSV download) and the search history.
"""

import os

from flask import (Blueprint, abort, g, redirect, render_template, request,
                   send_file)

from src.cli import CLI, LIST_LABELS
from src.discovery import SORT_OPTIONS
from src.exporter import Exporter, ExportError
from src.tmdb_client import TmdbError

bp = Blueprint("main", __name__)

SORT_LABELS = {
    "rating": "คะแนน",
    "votes": "จำนวนโหวต",
    "year": "ปีใหม่ก่อน",
    "popularity": "ความนิยม",
}

# Messages shown after an add/remove action (Post -> Redirect -> Get).
ACTION_NOTICES = {
    ("added", "watchlist"): "เพิ่มเข้าสู่รายการรับชมแล้ว",
    ("added", "favorites"): "เพิ่มเข้าสู่รายการโปรดแล้ว",
    ("exists", "watchlist"): "เรื่องนี้อยู่ในรายการรับชมอยู่แล้ว",
    ("exists", "favorites"): "เรื่องนี้อยู่ในรายการโปรดอยู่แล้ว",
    ("removed", "watchlist"): "ลบออกจากรายการรับชมแล้ว",
    ("removed", "favorites"): "ลบออกจากรายการโปรดแล้ว",
    ("missing", "watchlist"): "ไม่พบเรื่องนี้ในรายการรับชม (อาจถูกลบไปแล้ว)",
    ("missing", "favorites"): "ไม่พบเรื่องนี้ในรายการโปรด (อาจถูกลบไปแล้ว)",
    ("error", "nodata"): (
        "เพิ่มไม่สำเร็จ: ไม่มีข้อมูลหนังในเครื่อง "
        "และโหมดนี้ไม่มีคีย์ TMDB"
    ),
}


def get_services():
    """Return the per-request service bundle (ready before every request)."""
    return g.services


def _notice_from_args():
    """Pick up the action message a redirect may have attached."""
    for (key, kind), text in ACTION_NOTICES.items():
        if request.args.get(key) == kind:
            return text
    return None


def _with(path, param):
    """Append one query parameter to a local path (? or & as needed)."""
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}{param}"


def _safe_target(default):
    """Return the form's ``next`` path when it is a local URL.

    Rejects absolute URLs and protocol-relative tricks (``//host`` and
    ``/\\host``), so the redirect can never leave this application.
    """
    target = (request.form.get("next") or "").strip()
    if ("\\" in target or not target.startswith("/")
            or target.startswith("//")):
        return default
    return target


def _parse_list_filters(args):
    """Read the similar-list filters; invalid values fall back + note."""
    filters = {"min_rating": 0.0, "min_votes": 0, "year_from": None,
               "year_to": None, "sort": "rating", "limit": 10}
    notes = []

    def read_number(name, cast, low, high, label):
        """Parse one numeric field, or fall back with a note."""
        raw = (args.get(name) or "").strip()
        if not raw:
            return None, None
        try:
            value = cast(raw)
        except ValueError:
            return None, f"ค่า{label}ไม่ใช่ตัวเลข — ใช้ค่าเริ่มต้นแทน"
        if not low <= value <= high:
            return None, f"ค่า{label}อยู่นอกช่วงที่รองรับ — ใช้ค่าเริ่มต้นแทน"
        return value, None

    value, note = read_number("min_rating", float, 0.0, 10.0, "คะแนนขั้นต่ำ")
    if note:
        notes.append(note)
    else:
        filters["min_rating"] = value if value is not None else 0.0

    value, note = read_number("min_votes", int, 0, 10 ** 7, "โหวตขั้นต่ำ")
    if note:
        notes.append(note)
    else:
        filters["min_votes"] = value if value is not None else 0

    value, note = read_number("year_from", int, 1900, 2100, "ปีเริ่มต้น")
    if note:
        notes.append(note)
    else:
        filters["year_from"] = value

    value, note = read_number("year_to", int, 1900, 2100, "ปีสิ้นสุด")
    if note:
        notes.append(note)
    else:
        filters["year_to"] = value

    if (filters["year_from"] and filters["year_to"]
            and filters["year_from"] > filters["year_to"]):
        filters["year_from"], filters["year_to"] = (
            filters["year_to"], filters["year_from"])
        notes.append("ช่วงปีสลับกัน — สลับให้จากน้อยไปมากแล้ว")

    sort = (args.get("sort") or "").strip()
    if sort:
        if sort in SORT_OPTIONS:
            filters["sort"] = sort
        else:
            notes.append("ไม่รู้จักวิธีเรียงที่เลือก — ใช้ 'rating' แทน")

    value, note = read_number("limit", int, 1, 20, "จำนวนรายการ")
    if note:
        notes.append(note)
    else:
        filters["limit"] = value if value is not None else 10

    return filters, notes


def _movie_not_found(tmdb_id):
    """Render the polite 'movie not found' page for a bad TMDB id."""
    return render_template(
        "error.html",
        title="ไม่พบภาพยนตร์เรื่องนี้ (404)",
        message=f"รหัสภาพยนตร์ {tmdb_id} ไม่มีใน TMDB — "
                "ตรวจสอบรหัสแล้วลองใหม่",
    ), 404


def _add_to_list(kind, tmdb_id):
    """Shared handler: add by id, then redirect back with a result flag."""
    builder = get_services()["builder"]
    try:
        if kind == "watchlist":
            added = builder.add(tmdb_id)
        else:
            added = builder.add_favorite(tmdb_id)
    except TmdbError as exc:
        if "404" in str(exc):
            return _movie_not_found(tmdb_id)
        raise
    except ValueError:
        target = _safe_target(f"/movie/{tmdb_id}")
        return redirect(_with(target, "error=nodata"), code=303)
    flag = "added" if added else "exists"
    target = _safe_target(f"/movie/{tmdb_id}")
    return redirect(_with(target, f"{flag}={kind}"), code=303)


def _remove_from_list(kind, tmdb_id):
    """Shared handler: remove by id, then redirect back with a flag."""
    store = get_services()["store"]
    if kind == "watchlist":
        removed = store.remove_from_watchlist(tmdb_id)
    else:
        removed = store.remove_favorite(tmdb_id)
    flag = "removed" if removed else "missing"
    target = _safe_target(f"/movie/{tmdb_id}")
    return redirect(_with(target, f"{flag}={kind}"), code=303)


def _render_list(kind):
    """Render one list page (watchlist or favorites)."""
    services = get_services()
    store = services["store"]
    if kind == "watchlist":
        rows = store.get_watchlist()
        other_ids = {row["tmdb_id"] for row in store.get_favorites()}
        other_label = LIST_LABELS["favorites"]
    else:
        rows = store.get_favorites()
        other_ids = {row["tmdb_id"] for row in store.get_watchlist()}
        other_label = LIST_LABELS["watchlist"]
    notices = []
    notice = _notice_from_args()
    if notice:
        notices.append(notice)
    if request.args.get("cleared") == "watchlist":
        count = request.args.get("count", "0")
        notices.append(f"ล้างรายการรับชมเรียบร้อยแล้ว ({count} เรื่อง)")
    return render_template(
        "list.html",
        kind=kind,
        page_title=LIST_LABELS[kind],
        rows=rows,
        other_ids=other_ids,
        other_label=other_label,
        notices=notices,
    )


@bp.get("/")
def home():
    """Home page: search form and a short introduction."""
    return render_template("home.html")


@bp.get("/search")
def search():
    """Run the query through the discovery service and show movie cards."""
    services = get_services()
    query = (request.args.get("q") or "").strip()
    if not query:
        return render_template(
            "search.html",
            query="",
            notice="กรุณาพิมพ์คำค้นก่อนกดค้นหา",
        )
    notice = None
    max_length = 120  # กันคำค้นยาวผิดปกติ — ค้นเฉพาะส่วนแรก
    if len(query) > max_length:
        query = query[:max_length]
        notice = f"คำค้นยาวเกิน {max_length} ตัวอักษร — ค้นเฉพาะส่วนแรกให้"
    if services["client"] is None:
        return render_template(
            "search.html",
            query=query,
            notice=("ยังไม่ได้ตั้งค่าคีย์ TMDB — กำหนดตัวแปรสภาพแวดล้อม "
                    "TMDB_API_KEY แล้วเปิดเซิร์ฟเวอร์ใหม่ "
                    "(หน้าออฟไลน์ เช่นรายการรับชม · ประวัติ ยังใช้ได้ตามปกติ)"),
        )
    results = services["discovery"].search(query)
    return render_template("search.html", query=query,
                           results=results, notice=notice)


@bp.get("/movie/<int:tmdb_id>")
def movie(tmdb_id):
    """Movie details, similar movies (filterable) and list buttons."""
    services = get_services()
    client = services["client"]
    store = services["store"]
    notices = []
    notice = _notice_from_args()
    if notice:
        notices.append(notice)

    if client is not None:
        try:
            movie = client.get_movie_details(tmdb_id)
        except TmdbError as exc:
            if "404" in str(exc):
                return _movie_not_found(tmdb_id)
            raise
        store.add_movie(movie)
    else:
        movie = store.get_movie(tmdb_id)
        if movie is None:
            return render_template(
                "error.html",
                title="ไม่มีข้อมูลภาพยนตร์เรื่องนี้ในเครื่อง",
                message=("โหมดไม่มีคีย์ TMDB จะดูได้เฉพาะเรื่องที่บันทึกไว้แล้ว "
                         "— เปิดโหมดมีคีย์เพื่อค้นหาเรื่องใหม่"),
            ), 404
        notices.append("โหมดไม่มีคีย์ TMDB: แสดงข้อมูลที่บันทึกไว้ในเครื่อง")

    movie = dict(movie)
    movie.setdefault("id", tmdb_id)
    poster_path = movie.get("poster_path")
    backdrop_path = movie.get("backdrop_path")
    poster_url = (f"https://image.tmdb.org/t/p/w342{poster_path}"
                  if poster_path else None)
    backdrop_url = (f"https://image.tmdb.org/t/p/w780{backdrop_path}"
                    if backdrop_path else None)

    filters, notes = _parse_list_filters(request.args)
    notices.extend(notes)

    similar = []
    similar_error = None
    if client is None:
        for link in store.get_similar_links(tmdb_id):
            stored = store.get_movie(link["target_id"])
            if stored:
                stored.setdefault("id", link["target_id"])
                similar.append(stored)
    else:
        try:
            similar = services["discovery"].find_similar(
                tmdb_id,
                min_rating=filters["min_rating"],
                min_votes=filters["min_votes"],
                year_from=filters["year_from"],
                year_to=filters["year_to"],
                limit=filters["limit"],
                sort=filters["sort"],
            )
        except TmdbError as exc:
            similar_error = CLI.describe_tmdb_error(exc)

    year = (movie.get("release_date") or "")[:4] or None
    return render_template(
        "movie.html",
        movie=movie,
        year=year,
        poster_url=poster_url,
        backdrop_url=backdrop_url,
        genres=movie.get("genres") or [],
        runtime=movie.get("runtime"),
        filters=filters,
        sorts=SORT_OPTIONS,
        sort_labels=SORT_LABELS,
        notices=notices,
        similar=similar,
        similar_error=similar_error,
        in_watchlist=store.is_in_watchlist(tmdb_id),
        in_favorites=store.is_in_favorites(tmdb_id),
    )


@bp.get("/watchlist")
def watchlist():
    """Show the watchlist with cross-list stars and CSV download."""
    return _render_list("watchlist")


@bp.get("/favorites")
def favorites():
    """Show favorites with cross-list stars and CSV download."""
    return _render_list("favorites")


@bp.get("/history")
def history():
    """Show the most recent searches (newest first)."""
    limit_raw = (request.args.get("limit") or "").strip()
    limit = 10
    if limit_raw:
        try:
            limit = max(1, min(int(limit_raw), 50))
        except ValueError:
            limit = 10
    rows = get_services()["store"].get_recent_searches(limit)
    return render_template("history.html", rows=rows, limit=limit)


@bp.get("/export/<kind>")
def export_list(kind):
    """Download the current list as a CSV file (written by Exporter)."""
    if kind not in LIST_LABELS:
        abort(404)
    services = get_services()
    path = os.path.join(services["data_dir"], f"{kind}.csv")
    try:
        if kind == "watchlist":
            Exporter.export_watchlist(services["store"], path)
        else:
            Exporter.export_favorites(services["store"], path)
    except ExportError as exc:
        return render_template(
            "error.html",
            title="สร้างไฟล์ CSV ไม่สำเร็จ",
            message=f"เขียนไฟล์ไม่สำเร็จ: {exc}",
        ), 500
    return send_file(path, as_attachment=True,
                     download_name=f"{kind}.csv", mimetype="text/csv")


@bp.post("/watchlist/add/<int:tmdb_id>")
def watchlist_add(tmdb_id):
    """Add one movie to the watchlist, then return to the page."""
    return _add_to_list("watchlist", tmdb_id)


@bp.post("/watchlist/remove/<int:tmdb_id>")
def watchlist_remove(tmdb_id):
    """Remove one movie from the watchlist, then return to the page."""
    return _remove_from_list("watchlist", tmdb_id)


@bp.post("/watchlist/clear")
def watchlist_clear():
    """Clear the whole watchlist, then return with a count notice."""
    count = get_services()["store"].clear_watchlist()
    target = _safe_target("/watchlist")
    return redirect(_with(target, f"cleared=watchlist&count={count}"),
                    code=303)


@bp.post("/favorites/add/<int:tmdb_id>")
def favorites_add(tmdb_id):
    """Add one movie to favorites, then return to the page."""
    return _add_to_list("favorites", tmdb_id)


@bp.post("/favorites/remove/<int:tmdb_id>")
def favorites_remove(tmdb_id):
    """Remove one movie from favorites, then return to the page."""
    return _remove_from_list("favorites", tmdb_id)
