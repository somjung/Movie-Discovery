"""Interactive command-line front-end for the Movie Discovery app.

Sprint 1 scope (presentation layer only): welcome banner, command menu,
input handling (``.strip().lower()``), input validation, and graceful
exits.  ``search`` / ``discover`` are simulated with the built-in sample
dataset; the TMDB-backed services arrive in Sprint 2.
"""

from .sample_data import SAMPLE_MOVIES

WELCOME_MESSAGE = """\
============================================================
  Movie Discovery & Watchlist Builder — CLI (Sprint 1)
  ระบบค้นพบภาพยนตร์และสร้างรายการรับชม
============================================================"""

MENU_TEXT = """\
คำสั่งที่ใช้ได้:
  search <ชื่อเรื่อง>      ค้นหาภาพยนตร์จากชื่อเรื่อง (ข้อมูลตัวอย่าง)
  discover <รหัส>         แสดงภาพยนตร์ที่คล้ายกัน (ข้อมูลตัวอย่าง)
  watchlist add <รหัส>    เพิ่มภาพยนตร์เข้ารายการรับชม
  watchlist list          แสดงรายการรับชม
  watchlist clear         ล้างรายการรับชม
  help                    แสดงคำสั่งทั้งหมด
  quit / exit / ออก       ออกจากโปรแกรม"""

FAREWELL_MESSAGE = "ขอบคุณที่ใช้งานโปรแกรม ลาก่อน"
QUIT_COMMANDS = {"quit", "exit", "q", "ออก"}


class CLI:
    """Presentation layer of the project (menus + input validation)."""

    def __init__(self, input_func=input, output_func=print):
        self.input_func = input_func
        self.output_func = output_func
        self.watchlist = []  # session-only in Sprint 1 (SQLite arrives in Sprint 3)
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
        """search <ชื่อเรื่อง> — find sample movies containing the text."""
        if not args:
            raise ValueError("คำสั่ง search ต้องระบุชื่อเรื่อง เช่น search alpha")
        query = " ".join(args)
        matches = [
            movie for movie in SAMPLE_MOVIES if query in movie["title"].lower()
        ]
        if not matches:
            self.output_func(
                f"ไม่พบภาพยนตร์ที่ตรงกับ '{query}' ในข้อมูลตัวอย่าง"
            )
            return
        self.output_func(f"พบ {len(matches)} เรื่อง:")
        for movie in matches:
            self.output_func("  " + self.format_movie(movie))

    def cmd_discover(self, args):
        """discover <รหัส> — list sample movies 'similar' to the seed id."""
        if not args:
            raise ValueError(
                "คำสั่ง discover ต้องระบุรหัสภาพยนตร์ เช่น discover 101"
            )
        seed_id = self.parse_positive_int(args[0], "รหัสภาพยนตร์")
        seed = next(
            (movie for movie in SAMPLE_MOVIES if movie["id"] == seed_id), None
        )
        if seed is None:
            self.output_func(f"ไม่พบรหัสภาพยนตร์ {seed_id} ในข้อมูลตัวอย่าง")
            return
        others = sorted(
            (m for m in SAMPLE_MOVIES if m["id"] != seed_id),
            key=lambda m: (m["vote_average"] or 0, m["vote_count"] or 0),
            reverse=True,
        )
        self.output_func(
            f"ภาพยนตร์ที่คล้ายกับ '{seed['title']}' (ข้อมูลตัวอย่าง):"
        )
        for rank, movie in enumerate(others[:5], start=1):
            self.output_func(f"  {rank}. {self.format_movie(movie)}")

    def cmd_watchlist(self, args):
        """watchlist add <รหัส> | list | clear — manage the watchlist."""
        if not args:
            raise ValueError(
                "คำสั่ง watchlist ต้องมีคำสั่งย่อย: add <รหัส> | list | clear"
            )
        action, rest = args[0], args[1:]
        if action == "list":
            self.show_watchlist()
        elif action == "add":
            self.add_to_watchlist(rest)
        elif action == "clear":
            self.watchlist.clear()
            self.output_func("ล้างรายการรับชมเรียบร้อยแล้ว")
        else:
            raise ValueError(
                f"ไม่รู้จักคำสั่งย่อย '{action}' (ใช้ add <รหัส> | list | clear)"
            )

    # ---------- helpers ----------

    def show_watchlist(self):
        """Print the current session watchlist."""
        if not self.watchlist:
            self.output_func("รายการรับชมยังว่างอยู่ (ใช้ watchlist add <รหัส>)")
            return
        self.output_func(f"รายการรับชม ({len(self.watchlist)} เรื่อง):")
        for movie in self.watchlist:
            self.output_func("  " + self.format_movie(movie))

    def add_to_watchlist(self, rest):
        """Add one sample movie id to the watchlist (no duplicates)."""
        if not rest:
            raise ValueError(
                "คำสั่ง watchlist add ต้องระบุรหัสภาพยนตร์ เช่น watchlist add 101"
            )
        movie_id = self.parse_positive_int(rest[0], "รหัสภาพยนตร์")
        movie = next((m for m in SAMPLE_MOVIES if m["id"] == movie_id), None)
        if movie is None:
            self.output_func(f"ไม่พบรหัสภาพยนตร์ {movie_id} ในข้อมูลตัวอย่าง")
            return
        if any(m["id"] == movie_id for m in self.watchlist):
            self.output_func(f"'{movie['title']}' อยู่ในรายการรับชมแล้ว")
            return
        self.watchlist.append(movie)
        self.output_func(f"เพิ่ม '{movie['title']}' เข้ารายการรับชมแล้ว")

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
        year = (movie.get("release_date") or "")[:4] or "----"
        rating = movie.get("vote_average")
        rating_text = "-" if rating is None else f"{rating:.1f}"
        return f"[{movie['id']}] {movie['title']} ({year}) คะแนน {rating_text}"
