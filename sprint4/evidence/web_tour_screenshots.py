"""Real-browser tour of the Sprint 4 web app, driven through CDP.

Runs against the Chrome instance started with
``--remote-debugging-port=9222`` (profile ``chrome_sfp``), walks the demo
flow the same way a user would (click the card, submit the buttons), and
saves 1600x900 PNG screenshots plus a JSON step log for the deck/report.

The two AI steps make real DeepSeek calls (they are cached afterwards, so
re-running the tour costs nothing).

Run (from sprint4/evidence):
    uv run --with websocket-client --no-project python web_tour_screenshots.py
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.request

from websocket import create_connection

CDP = "http://127.0.0.1:9222"
APP = "http://127.0.0.1:5000"
HERE = os.path.dirname(os.path.abspath(__file__))
SHOT_DIR = os.path.join(HERE, "screens-2026-10-14")

MOOD = "อยากดูอะไรเบา ๆ สนุก ๆ ไม่เครียด"
STEPS = []


def log(message: str) -> None:
    print(message, flush=True)


def record(name: str, **fields) -> None:
    entry = {"step": name, **fields}
    STEPS.append(entry)


def connect_page():
    targets = json.load(urllib.request.urlopen(CDP + "/json/list"))
    pages = [t for t in targets
             if t.get("type") == "page" and "127.0.0.1:5000" in t.get("url", "")]
    if not pages:
        raise RuntimeError("no app page found on the CDP endpoint")
    return create_connection(pages[0]["webSocketDebuggerUrl"], timeout=60,
                             suppress_origin=True)


class Session:
    def __init__(self, ws):
        self.ws = ws
        self.counter = 0

    def send(self, method: str, params: dict | None = None):
        self.counter += 1
        mid = self.counter
        self.ws.send(json.dumps({"id": mid, "method": method,
                                 "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def js(self, expression: str):
        out = self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        })
        return out.get("result", {}).get("value")

    def wait_for(self, condition: str, timeout: float, label: str) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if self.js(condition):
                    return True
            except RuntimeError:
                pass
            time.sleep(0.4)
        log(f"  !! timeout waiting for: {label}")
        return False

    def wait_ready(self, timeout: float = 20) -> bool:
        return self.wait_for("document.readyState === 'complete'",
                             timeout, "readyState complete")

    def nav(self, path: str, timeout: float = 25) -> None:
        self.send("Page.navigate", {"url": APP + path})
        self.wait_ready(timeout)

    def settle(self, timeout: float = 12.0) -> None:
        """Wait for visible images/fonts so screenshots never catch blanks."""
        try:
            self.js("document.fonts.ready.then(() => true)")
        except RuntimeError:
            pass
        self.wait_for(
            "(() => { const vh = window.innerHeight;"
            " return [...document.images]"
            "   .filter(i => i.getBoundingClientRect().top < vh + 250)"
            "   .every(i => i.complete); })()",
            timeout, "visible images complete")
        time.sleep(0.5)

    def shot(self, name: str) -> str:
        self.settle()
        data = self.send("Page.captureScreenshot", {"format": "png"})["data"]
        path = os.path.join(SHOT_DIR, name)
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(data))
        size = os.path.getsize(path)
        log(f"  shot {name} ({size:,} bytes)")
        return path

    def title(self) -> str:
        return self.js("document.title") or ""


def main() -> int:
    os.makedirs(SHOT_DIR, exist_ok=True)
    session = Session(connect_page())
    session.send("Page.enable")
    session.send("Runtime.enable")
    session.send("Emulation.setDeviceMetricsOverride", {
        "width": 1600, "height": 900, "deviceScaleFactor": 1, "mobile": False,
    })

    log("== tour: home ==")
    session.nav("/", 30)
    session.shot("01-home.png")
    record("home", title=session.title())

    log("== tour: search 'inception' ==")
    session.nav("/search?q=inception", 30)
    session.wait_for(
        "document.querySelectorAll('a[href^=\"/movie/\"]').length > 0",
        20, "search result cards")
    cards = session.js("document.querySelectorAll('a[href^=\"/movie/\"]').length")
    session.shot("02-search-results.png")
    record("search", cards=cards, title=session.title())

    log("== tour: open movie 27205 by clicking its card ==")
    clicked = session.js(
        "(() => { const a = [...document.querySelectorAll('a[href=\"/movie/27205\"]')][0];"
        " if (!a) return 'not-found'; a.click(); return 'clicked'; })()")
    record("card-click", result=clicked)
    session.wait_for(
        "location.pathname === '/movie/27205' && document.readyState === 'complete'",
        25, "movie details page")
    session.wait_for(
        "!!document.querySelector('form[action=\"/watchlist/add/27205\"]')",
        15, "details buttons")
    session.shot("03-movie-details.png")
    record("details", title=session.title())

    log("== tour: AI Thai summary (real DeepSeek call) ==")
    started = time.time()
    session.nav("/movie/27205?summary=1", 40)
    found = session.wait_for("!!document.querySelector('.ai-summary')", 45,
                             "ai summary block")
    took = round(time.time() - started, 1)
    excerpt = session.js(
        "((document.querySelector('.ai-summary') || {}).innerText || '')"
        ".slice(0, 160)")
    session.shot("04-movie-ai-summary.png")
    record("summary", found=found, seconds=took, excerpt=excerpt)

    log("== tour: add Inception to the watchlist ==")
    session.js("(() => { const f = document.querySelector('form[action=\"/watchlist/add/27205\"]');"
               " if (!f) return 'no-form'; f.submit(); return 'submitted'; })()")
    session.wait_ready(25)
    time.sleep(0.5)
    notice = session.js("(() => { const n = document.querySelector('.notice');"
                        " return n ? n.innerText : ''; })()")
    session.shot("05-movie-added-notice.png")
    record("add-to-watchlist", notice=notice)

    log("== tour: watchlist page ==")
    session.nav("/watchlist", 25)
    session.wait_for("document.body.innerText.includes('Inception')", 15,
                     "Inception row")
    session.shot("06-watchlist.png")
    record("watchlist", title=session.title())

    log("== tour: AI recommend form ==")
    session.nav("/ai/recommend", 25)
    session.wait_for("!!document.querySelector('form.ai-form select[name=base]')",
                     15, "recommend form")
    session.shot("07-ai-recommend-form.png")
    option_count = session.js(
        "document.querySelectorAll('form.ai-form select[name=base] option').length")
    record("recommend-form", options=option_count)

    log("== tour: submit recommend (seed=27205 + mood, real DeepSeek call) ==")
    started = time.time()
    submitted = session.js(
        "(() => { const f = document.querySelector('form.ai-form');"
        " const s = f.querySelector('select[name=base]');"
        " s.value = '27205';"
        " if (s.value !== '27205') return 'option-missing';"
        f" f.querySelector('input[name=mood]').value = {json.dumps(MOOD)};"
        " f.submit(); return 'submitted'; })()")
    record("recommend-submit", result=submitted)
    found = session.wait_for("!!document.querySelector('.result-count')", 75,
                             "recommend results")
    took = round(time.time() - started, 1)
    heading = session.js(
        "(() => { const h = document.querySelector('.result-count');"
        " return h ? h.innerText : ''; })()")
    first_reason = session.js(
        "(() => { const r = document.querySelector('.ai-reason');"
        " return r ? r.innerText : ''; })()")
    session.shot("08-ai-recommend-results.png")
    record("recommend-results", found=found, seconds=took,
           heading=heading, first_reason=first_reason)

    log("== tour: add the first AI pick to the watchlist ==")
    clicked = session.js(
        "(() => { const b = document.querySelector('.ai-results form[action^=\"/watchlist/add/\"] button');"
        " if (!b) return 'no-button'; b.click(); return 'clicked'; })()")
    session.wait_ready(25)
    session.wait_for("!!document.querySelector('.result-count')", 30,
                     "results page again")
    time.sleep(0.5)
    session.shot("09-ai-results-added.png")
    record("add-pick", result=clicked)

    log("== tour: watchlist (final) ==")
    session.nav("/watchlist", 25)
    session.wait_for("document.body.innerText.includes('Inception')", 15,
                     "watchlist rows")
    rows = session.js(
        "document.querySelectorAll('.watchlist .card, .cards .card, table tbody tr').length")
    session.shot("10-watchlist-final.png")
    record("watchlist-final", rows=rows)

    log("== tour: history ==")
    session.nav("/history", 25)
    time.sleep(0.6)
    session.shot("11-history.png")
    record("history", title=session.title())

    log_titles = session.js("document.body.innerText.replace(/\\s+/g, ' ').slice(0, 140)")
    record("final-page-text", sample=log_titles)

    with open(os.path.join(SHOT_DIR, "tour-log.json"), "w", encoding="utf-8") as fh:
        json.dump(STEPS, fh, ensure_ascii=False, indent=2)
    log(f"== done: {len(STEPS)} steps, screenshots in {SHOT_DIR} ==")
    session.ws.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
