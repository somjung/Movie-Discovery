"""Flask application factory for the web front-end (Sprint 3).

The web layer is a new presentation layer: it imports the Sprint 1-2
business and data services unchanged and turns page requests into calls
on the same objects the CLI uses.  ``client`` and ``store`` can be
injected so the test-suite and local checks run fully offline.
"""

import sqlite3

from flask import Flask, g, render_template

from src.cli import CLI
from src.config import get_data_dir, get_db_path
from src.discovery import DiscoveryService
from src.movie_store import MovieStore
from src.tmdb_client import TmdbClient, TmdbError
from src.watchlist import WatchlistBuilder


TMDB_ATTRIBUTION = (
    "This product uses the TMDB API but is not endorsed or certified by TMDB."
)

DB_HELP = (
    "วิธีแก้: ปิดเซิร์ฟเวอร์ · ย้ายหรือลบไฟล์ฐานข้อมูลด้านบน "
    "(ระบบจะสร้างไฟล์ใหม่ให้อัตโนมัติเมื่อเปิดเซิร์ฟเวอร์อีกครั้ง) "
    "แล้วเริ่มใช้งานใหม่"
)


def create_app(client=None, store=None, data_dir=None, db_path=None):
    """Build the web app; inject ``client``/``store`` to run offline (tests).

    Production mode builds one service bundle per request, each with its
    own SQLite connection: Python's sqlite3 refuses a connection created
    in one thread being used from another, and Flask's development server
    handles requests in worker threads.  Injected objects (tests) are
    reused as-is, keeping everything in the test thread and allowing an
    in-memory database to survive across requests.
    """
    app = Flask(__name__)
    app.config["DATA_DIR"] = data_dir or get_data_dir()
    app.config["DB_PATH"] = db_path or get_db_path()

    def database_error_page(exc):
        """Polite page for an unreadable database file (with repair steps)."""
        return render_template(
            "error.html",
            title="ฐานข้อมูลมีปัญหา",
            message=(
                f"เปิดไฟล์ฐานข้อมูลไม่สำเร็จ: {exc} · "
                f"ไฟล์: {app.config['DB_PATH']} — {DB_HELP}"
            ),
        ), 500

    def build_services():
        """Create the service bundle for one request."""
        if store is not None or client is not None:
            test_store = store if store is not None else MovieStore(":memory:")
            return {
                "store": test_store,
                "client": client,
                "discovery": (DiscoveryService(client, test_store)
                              if client is not None else None),
                "builder": WatchlistBuilder(test_store, client),
                "key_missing": client is None,
                "data_dir": app.config["DATA_DIR"],
                "close_store": False,
            }
        request_store = MovieStore(app.config["DB_PATH"])
        request_client = None
        key_missing = False
        try:
            request_client = TmdbClient(store=request_store)
        except RuntimeError:
            key_missing = True
        return {
            "store": request_store,
            "client": request_client,
            "discovery": (DiscoveryService(request_client, request_store)
                          if request_client is not None else None),
            "builder": WatchlistBuilder(request_store, request_client),
            "key_missing": key_missing,
            "data_dir": app.config["DATA_DIR"],
            "close_store": True,
        }

    @app.before_request
    def load_services():
        """Prepare the per-request services before every page.

        A damaged database file fails here (connection + table setup);
        the request stops early with a polite repair page instead of a
        raw traceback.
        """
        try:
            g.services = build_services()
        except sqlite3.Error as exc:
            g.services = None
            return database_error_page(exc)

    @app.teardown_request
    def close_services(exc):
        """Close the request's SQLite connection when the request ends."""
        bundle = g.pop("services", None)
        if bundle is not None and bundle["close_store"]:
            bundle["store"].close()

    from .routes import bp, playable_ids
    app.register_blueprint(bp)

    @app.errorhandler(TmdbError)
    def handle_tmdb_error(exc):
        """Map TMDB failures to a polite error page (CLI wording reused)."""
        return render_template("error.html",
                               title="เชื่อมต่อ TMDB ไม่สำเร็จ",
                               message=CLI.describe_tmdb_error(exc)), 502

    @app.errorhandler(sqlite3.Error)
    def handle_database_error(exc):
        """Fallback page when the database fails during a request."""
        return database_error_page(exc)

    @app.errorhandler(404)
    def handle_not_found(exc):
        """Show a friendly page for unknown URLs."""
        return render_template(
            "error.html",
            title="ไม่พบหน้าที่ต้องการ (404)",
            message="ลิงก์อาจไม่ถูกต้อง หรือหน้านี้ยังไม่เปิดใช้งาน",
        ), 404

    @app.context_processor
    def inject_nav_state():
        """Give every page the list counts and the playable-movie ids."""
        bundle = getattr(g, "services", None)
        if bundle is None:
            # Database error path: neutral navigation, no key banner.
            return {
                "nav_watchlist": 0,
                "nav_favorites": 0,
                "key_missing": False,
                "playable_ids": frozenset(),
                "tmdb_attribution": TMDB_ATTRIBUTION,
            }
        return {
            "nav_watchlist": len(bundle["store"].get_watchlist()),
            "nav_favorites": len(bundle["store"].get_favorites()),
            "key_missing": bundle["key_missing"],
            "playable_ids": playable_ids(bundle["data_dir"]),
            "tmdb_attribution": TMDB_ATTRIBUTION,
        }

    return app
