"""Interactive command-line front-end for the Movie Discovery app.

Sprint 2 scope: the presentation layer is now wired to the real back-end —
TMDB (with caching) for search/discover, SQLite for watchlist/favorites/
search history, and CSV export for the File I/O requirement.  Commands keep
the Sprint-1 Thai messages and validation; ``client`` and ``store`` can be
injected so the test-suite runs fully offline.
"""

import os

from .config import get_data_dir, get_db_path
from .discovery import SORT_OPTIONS, DiscoveryService
from .exporter import Exporter, ExportError
from .movie_store import MovieStore
from .tmdb_client import TmdbClient, TmdbError
from .watchlist import WatchlistBuilder

WELCOME_MESSAGE = """\
============================================================
  Movie Discovery & Watchlist Builder — CLI
  ระบบค้นพบภาพยนตร์และสร้างรายการรับชม
============================================================"""

MENU_TEXT = """\
คำสั่งที่ใช้ได้:
  search <ชื่อเรื่อง>              ค้นหาภาพยนตร์จาก TMDB
  discover <รหัส> [ตัวเลือก]       ภาพยนตร์ที่คล้ายกัน (กรอง/เรียงได้)
        --min-rating 0-10 · --min-votes N · --year YYYY|YYYY-YYYY
        --sort rating|votes|year|popularity · --limit N
  watchlist add <รหัส>            เพิ่มเข้ารายการรับชม
  watchlist list                  แสดงรายการรับชม
  watchlist remove <รหัส>         นำออกจากรายการรับชม
  watchlist clear                 ล้างรายการรับชมทั้งหมด
  favorites add <รหัส>            เพิ่มเข้ารายการโปรด
  favorites list                  แสดงรายการโปรด
  favorites remove <รหัส>         นำออกจากรายการโปรด
  export watchlist|favorites      ส่งออกรายการเป็น CSV (โฟลเดอร์ data/)
  history [จำนวน]                 ประวัติการค้นหาล่าสุด (ค่าเริ่มต้น 10)
  help                            แสดงคำสั่งทั้งหมด
  quit / exit / ออก               ออกจากโปรแกรม"""

FAREWELL_MESSAGE = "ขอบคุณที่ใช้งานโปรแกรม ลาก่อน"
QUIT_COMMANDS = {"quit", "exit", "q", "ออก"}

MISSING_KEY_MESSAGE = (
    "ยังไม่ได้ตั้งค่าคีย์ TMDB — กำหนดตัวแปรสภาพแวดล้อม TMDB_API_KEY "
    "ก่อนใช้งาน\n"
    "  · สร้างคีย์ฟรีได้ที่ https://developer.themoviedb.org/\n"
    "  · คำสั่งที่ไม่ใช้ TMDB (watchlist list, export, history, help) "
    "ยังใช้งานได้ตามปกติ"
)

DISCOVER_FLAGS = ("--min-rating", "--min-votes", "--year", "--sort", "--limit")

LIST_LABELS = {"watchlist": "รายการรับชม", "favorites": "รายการโปรด"}


class CLI:
    """Presentation layer of the project (menus + input validation)."""

    def __init__(self, input_func=input, output_func=print, client=None,
                 store=None, db_path=None, data_dir=None):
        """Wire the CLI; inject ``client``/``store`` to run offline (tests).

        Without a ``client`` the real TMDB client is built from
        ``TMDB_API_KEY``; when the key is missing the CLI still starts and
        only the TMDB-backed commands become unavailable.
        """
        self.input_func = input_func
        self.output_func = output_func
        self.store = (store if store is not None
                      else MovieStore(db_path or get_db_path()))
        self.data_dir = data_dir or get_data_dir()
        self.key_missing = False
        if client is not None:
            self.client = client
        else:
            try:
                self.client = TmdbClient(store=self.store)
            except RuntimeError:
                self.client = None
                self.key_missing = True
        self.discovery = (DiscoveryService(self.client, self.store)
                          if self.client is not None else None)
        self.builder = WatchlistBuilder(self.store, self.client)
        self.running = False

    # ---------- display ----------

    def display_welcome_message(self):
        """Show the welcome banner."""
        self.output_func(WELCOME_MESSAGE)

    def display_menu(self):
        """Show the list of available commands."""
        self.output_func(MENU_TEXT)

    # ---------- input ----------

    def get_command_input(self):
        """Read one command line and normalise it (strip + lowercase)."""
        raw = self.input_func("movie> ")
        return raw.strip().lower()

    # ---------- main loop ----------

    def run(self):
        """Main loop: read -> validate -> dispatch, without ever crashing."""
        self.display_welcome_message()
        self.display_menu()
        self.running = True
        while self.running:
            try:
                self.handle_command(self.get_command_input())
            except EOFError:
                self.output_func("")
                self.output_func("[สิ้นสุดอินพุต]")
                self.running = False
            except KeyboardInterrupt:
                self.output_func("")
                self.output_func("[ยกเลิกโดยผู้ใช้]")
                self.running = False
            except ValueError as exc:
                self.output_func(f"คำเตือน: {exc}")
            except TmdbError as exc:
                self.output_func(self.describe_tmdb_error(exc))
            except ExportError as exc:
                self.output_func(f"ไม่สามารถเขียนไฟล์ได้: {exc}")
        self.output_func(FAREWELL_MESSAGE)

    def handle_command(self, text):
        """Validate and dispatch one normalised command line."""
        if not text:
            raise ValueError("กรุณาพิมพ์คำสั่ง (พิมพ์ help เพื่อดูคำสั่งทั้งหมด)")
        parts = text.split()
        name, args = parts[0], parts[1:]
        if name in QUIT_COMMANDS:
            self.running = False
            return
        handlers = {
            "search": self.cmd_search,
            "discover": self.cmd_discover,
            "watchlist": self.cmd_watchlist,
            "favorites": self.cmd_favorites,
            "export": self.cmd_export,
            "history": self.cmd_history,
            "help": self.cmd_help,
        }
        handler = handlers.get(name)
        if handler is None:
            raise ValueError(
                f"ไม่รู้จักคำสั่ง '{name}' (พิมพ์ help เพื่อดูคำสั่งทั้งหมด)"
            )
        handler(args)

    # ---------- command handlers ----------

    def cmd_help(self, args):
        """help — show the command menu again."""
        self.display_menu()

    def cmd_search(self, args):
        """search <ชื่อเรื่อง> — search TMDB (cached) and log the query."""
        if not args:
            raise ValueError("คำสั่ง search ต้องระบุชื่อเรื่อง เช่น search alpha")
        if self.client is None:
            self.output_func(MISSING_KEY_MESSAGE)
            return
        query = " ".join(args)
        results = self.discovery.search(query)
        if not results:
            self.output_func(f"ไม่พบภาพยนตร์ที่ตรงกับ '{query}'")
            return
        self.output_func(f"พบ {len(results)} เรื่อง (แสดงสูงสุด 10 รายการแรก):")
        for movie in results:
            self.output_func("  " + self.format_movie(movie))

    def cmd_discover(self, args):
        """discover <รหัส> [ตัวเลือก] — similar movies, filtered and sorted."""
        if not args:
            raise ValueError(
                "คำสั่ง discover ต้องระบุรหัสภาพยนตร์ เช่น discover 101"
            )
        seed_id = self.parse_positive_int(args[0], "รหัสภาพยนตร์")
        options = self.parse_discover_options(args[1:])
        if self.client is None:
            self.output_func(MISSING_KEY_MESSAGE)
            return
        try:
            seed = self.builder.ensure_movie(seed_id)
        except TmdbError as exc:
            if "404" in str(exc):
                self.output_func(f"ไม่พบรหัสภาพยนตร์ {seed_id} ใน TMDB")
                return
            raise
        results = self.discovery.find_similar(
            seed_id,
            min_rating=options["min_rating"],
            min_votes=options["min_votes"],
            year_from=options["year_from"],
            year_to=options["year_to"],
            limit=options["limit"],
            sort=options["sort"],
        )
        if not results:
            self.output_func(
                f"ไม่พบภาพยนตร์ที่ผ่านเงื่อนไขสำหรับรหัส {seed_id}"
            )
            return
        self.output_func(
            f"ภาพยนตร์ที่คล้ายกับ '{seed['title']}' "
            f"({len(results)} เรื่อง · เรียงตาม {options['sort']}):"
        )
        for rank, movie in enumerate(results, start=1):
            self.output_func(f"  {rank}. {self.format_movie(movie)}")

    def cmd_watchlist(self, args):
        """watchlist add <รหัส> | list | remove <รหัส> | clear."""
        if not args:
            raise ValueError(
                "คำสั่ง watchlist ต้องมีคำสั่งย่อย: "
                "add <รหัส> | list | remove <รหัส> | clear"
            )
        action, rest = args[0], args[1:]
        if action == "list":
            self.show_list("watchlist")
        elif action == "add":
            self.add_to_list("watchlist", rest)
        elif action == "remove":
            self.remove_from_list("watchlist", rest)
        elif action == "clear":
            count = self.store.clear_watchlist()
            self.output_func(f"ล้างรายการรับชมเรียบร้อยแล้ว ({count} เรื่อง)")
        else:
            raise ValueError(
                f"ไม่รู้จักคำสั่งย่อย '{action}' "
                "(ใช้ add <รหัส> | list | remove <รหัส> | clear)"
            )

    def cmd_favorites(self, args):
        """favorites add <รหัส> | list | remove <รหัส>."""
        if not args:
            raise ValueError(
                "คำสั่ง favorites ต้องมีคำสั่งย่อย: "
                "add <รหัส> | list | remove <รหัส>"
            )
        action, rest = args[0], args[1:]
        if action == "list":
            self.show_list("favorites")
        elif action == "add":
            self.add_to_list("favorites", rest)
        elif action == "remove":
            self.remove_from_list("favorites", rest)
        else:
            raise ValueError(
                f"ไม่รู้จักคำสั่งย่อย '{action}' "
                "(ใช้ add <รหัส> | list | remove <รหัส>)"
            )

    def cmd_export(self, args):
        """export watchlist|favorites — write the list to CSV under data/."""
        if not args or args[0] not in LIST_LABELS:
            raise ValueError(
                "คำสั่ง export ต้องระบุรายการ: "
                "export watchlist หรือ export favorites"
            )
        kind = args[0]
        path = os.path.join(self.data_dir, f"{kind}.csv")
        if kind == "watchlist":
            count = Exporter.export_watchlist(self.store, path)
        else:
            count = Exporter.export_favorites(self.store, path)
        self.output_func(f"ส่งออก {count} รายการไปที่ {path}")

    def cmd_history(self, args):
        """history [N] — show the most recent searches (default 10)."""
        limit = 10
        if args:
            limit = self.parse_positive_int(args[0], "จำนวนรายการ")
        rows = self.store.get_recent_searches(limit)
        if not rows:
            self.output_func("ยังไม่มีประวัติการค้นหา")
            return
        self.output_func(f"ประวัติการค้นหาล่าสุด ({len(rows)} รายการ):")
        for index, row in enumerate(rows, start=1):
            self.output_func(
                f"  {index}. '{row['query']}' — พบ {row['result_count']} ผล "
                f"({row['searched_at']})"
            )

    # ---------- list helpers ----------

    def show_list(self, kind):
        """Print one stored list (``watchlist`` or ``favorites``)."""
        label = LIST_LABELS[kind]
        rows = (self.store.get_watchlist() if kind == "watchlist"
                else self.store.get_favorites())
        if not rows:
            self.output_func(f"{label}ยังว่างอยู่ (ใช้ {kind} add <รหัส>)")
            return
        self.output_func(f"{label} ({len(rows)} เรื่อง):")
        for row in rows:
            self.output_func("  " + self.format_movie(row))

    def add_to_list(self, kind, rest):
        """Add one movie id to the watchlist or favorites (fetch if needed)."""
        label = LIST_LABELS[kind]
        if not rest:
            raise ValueError(
                f"คำสั่ง {kind} add ต้องระบุรหัสภาพยนตร์ เช่น {kind} add 101"
            )
        movie_id = self.parse_positive_int(rest[0], "รหัสภาพยนตร์")
        if self.client is None and self.store.get_movie(movie_id) is None:
            self.output_func(MISSING_KEY_MESSAGE)
            return
        try:
            movie = self.builder.ensure_movie(movie_id)
        except TmdbError as exc:
            if "404" in str(exc):
                self.output_func(f"ไม่พบรหัสภาพยนตร์ {movie_id} ใน TMDB")
                return
            raise
        if kind == "watchlist":
            added = self.builder.add(movie_id)
        else:
            added = self.builder.add_favorite(movie_id)
        if added:
            self.output_func(f"เพิ่ม '{movie['title']}' เข้า{label}แล้ว")
        else:
            self.output_func(f"'{movie['title']}' อยู่ใน{label}แล้ว")

    def remove_from_list(self, kind, rest):
        """Remove one movie id from the watchlist or favorites."""
        label = LIST_LABELS[kind]
        if not rest:
            raise ValueError(
                f"คำสั่ง {kind} remove ต้องระบุรหัสภาพยนตร์ เช่น "
                f"{kind} remove 101"
            )
        movie_id = self.parse_positive_int(rest[0], "รหัสภาพยนตร์")
        if kind == "watchlist":
            removed = self.store.remove_from_watchlist(movie_id)
        else:
            removed = self.store.remove_favorite(movie_id)
        if removed:
            movie = self.store.get_movie(movie_id)
            title = movie["title"] if movie else str(movie_id)
            self.output_func(f"นำ '{title}' ออกจาก{label}แล้ว")
        else:
            self.output_func(f"ไม่พบรหัสภาพยนตร์ {movie_id} ใน{label}")

    # ---------- option / value parsing ----------

    def parse_discover_options(self, tokens):
        """Parse discover flags (--min-rating ... --limit) into a dict."""
        options = {"min_rating": 0.0, "min_votes": 0, "year_from": None,
                   "year_to": None, "sort": "rating", "limit": 10}
        index = 0
        while index < len(tokens):
            flag = tokens[index]
            if flag not in DISCOVER_FLAGS:
                raise ValueError(
                    f"ไม่รู้จักตัวเลือก '{flag}' "
                    f"(ใช้ {' · '.join(DISCOVER_FLAGS)})"
                )
            if index + 1 >= len(tokens):
                raise ValueError(f"ตัวเลือก {flag} ต้องมีค่าตามหลัง")
            value = tokens[index + 1]
            if flag == "--min-rating":
                options["min_rating"] = self._parse_rating(value)
            elif flag == "--min-votes":
                options["min_votes"] = self._parse_non_negative_int(value)
            elif flag == "--year":
                options["year_from"], options["year_to"] = \
                    self._parse_year_range(value)
            elif flag == "--sort":
                if value not in SORT_OPTIONS:
                    raise ValueError(
                        f"--sort ต้องเป็น {', '.join(SORT_OPTIONS)} "
                        f"(ได้รับ '{value}')"
                    )
                options["sort"] = value
            else:  # --limit
                options["limit"] = self.parse_positive_int(value, "จำนวนรายการ")
            index += 2
        return options

    @staticmethod
    def _parse_rating(text):
        """Convert ``text`` to a 0–10 rating for --min-rating."""
        try:
            value = float(text)
        except ValueError:
            raise ValueError(
                f"ค่า --min-rating ต้องเป็นตัวเลข (ได้รับ '{text}')"
            ) from None
        if not 0.0 <= value <= 10.0:
            raise ValueError("ค่า --min-rating ต้องอยู่ระหว่าง 0 ถึง 10")
        return value

    @staticmethod
    def _parse_non_negative_int(text):
        """Convert ``text`` to a whole number >= 0 for --min-votes."""
        try:
            value = int(text)
        except ValueError:
            raise ValueError(
                f"ค่า --min-votes ต้องเป็นจำนวนเต็ม (ได้รับ '{text}')"
            ) from None
        if value < 0:
            raise ValueError("ค่า --min-votes ต้องไม่ติดลบ")
        return value

    @staticmethod
    def _parse_year_range(text):
        """Convert 'YYYY' or 'YYYY-YYYY' to a (year_from, year_to) pair."""
        parts = text.split("-")
        if len(parts) == 1:
            parts = [parts[0], parts[0]]
        if len(parts) != 2 or not all(
            len(part) == 4 and part.isdigit() for part in parts
        ):
            raise ValueError(
                "ค่า --year ต้องเป็นปี 4 หลัก เช่น 2020 หรือช่วง 1990-2020 "
                f"(ได้รับ '{text}')"
            )
        year_from, year_to = int(parts[0]), int(parts[1])
        if year_from > year_to:
            raise ValueError("ช่วงปีต้องเรียงจากน้อยไปมาก เช่น 1990-2020")
        return year_from, year_to

    # ---------- shared helpers ----------

    @staticmethod
    def describe_tmdb_error(exc):
        """Map a TmdbError to a friendly Thai message."""
        message = str(exc)
        if "401" in message:
            return "คีย์ TMDB ไม่ถูกต้องหรือถูกปฏิเสธ (401) — ตรวจสอบค่า TMDB_API_KEY"
        if "429" in message:
            return "เรียกใช้ TMDB ถี่เกินไป (429) — รอสักครู่แล้วลองใหม่"
        if "404" in message:
            return "ไม่พบข้อมูลที่ขอจาก TMDB (404)"
        return f"เชื่อมต่อ TMDB ไม่สำเร็จ: {message}"

    @staticmethod
    def parse_positive_int(text, label):
        """Convert text to a positive integer or raise a readable error."""
        try:
            value = int(text)
        except ValueError:
            raise ValueError(
                f"{label}ต้องเป็นตัวเลข (ได้รับ '{text}')"
            ) from None
        if value <= 0:
            raise ValueError(f"{label}ต้องมากกว่า 0 (ได้รับ {value})")
        return value

    @staticmethod
    def format_movie(movie):
        """Format one movie dict as a single display line."""
        movie_id = movie.get("id")
        if movie_id is None:
            movie_id = movie.get("tmdb_id")
        year = (movie.get("release_date") or "")[:4] or "----"
        rating = movie.get("vote_average")
        rating_text = "-" if rating is None else f"{rating:.1f}"
        return f"[{movie_id}] {movie['title']} ({year}) คะแนน {rating_text}"
