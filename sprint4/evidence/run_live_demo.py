"""Live DeepSeek evidence run for Sprint 4 (recommendations + Thai summaries).

Runs the real pipeline end-to-end against live APIs:
- TMDB: fetch the demo seed movie and its similar movies (real candidates)
- DeepSeek: pick recommendations (2 moods) + write Thai summaries (2 movies)

Everything runs through the project's own classes (TmdbClient,
DiscoveryService, AiClient, AiAdvisor).  A recording session captures the
latency and token usage of every AI call.  Output: a markdown evidence file
next to this script.

Secrets are read from the environment, the user registry or fallback files,
are never printed, and the evidence text is scanned for leak patterns
before it is written.
"""

import os
import pathlib
import re
import sys
import time
from datetime import datetime

import requests

APP_DIR = pathlib.Path(__file__).resolve().parent.parent / "script-final-project"
sys.path.insert(0, str(APP_DIR))

from src.ai_advisor import AiAdvisor  # noqa: E402
from src.ai_client import AiClient  # noqa: E402
from src.discovery import DiscoveryService  # noqa: E402
from src.movie_store import MovieStore  # noqa: E402
from src.tmdb_client import TmdbClient  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
HOME = pathlib.Path.home()

FALLBACKS = {
    "DEEPSEEK_API_KEY": [
        HOME / "AppData/Local/hermes/profiles/generalist/.env",
        HOME / "Downloads/Deepseek Api-key.txt",
    ],
    "TMDB_API_KEY": [
        HOME / "Downloads/Tmdb Api-key.txt",
    ],
}

MOOD_A = "อยากดูอะไรเบา ๆ สนุก ๆ ไม่เครียด"
MOOD_B = "อยากดูหนังตื่นเต้นชวนคิด"


def value_from_file(path, name):
    """Pull one value out of a .env-style file or a raw one-value file."""
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return None
    if path.name.endswith(".env"):
        for line in text.splitlines():
            line = line.strip()
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
        return None
    return text.splitlines()[0].strip()


def load_secret(name):
    """env -> user registry -> fallback files; returns how it was found."""
    if os.environ.get(name):
        return "environment"
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
        if value:
            os.environ[name] = value
            return "registry"
    except FileNotFoundError:
        pass
    for path in FALLBACKS.get(name, []):
        if path.exists():
            value = value_from_file(path, name)
            if value:
                os.environ[name] = value
                return "file: " + path.name
    return None


class RecordingSession(requests.Session):
    """Requests session that records latency + token usage per AI call."""

    def __init__(self):
        super().__init__()
        self.records = []

    def post(self, *args, **kwargs):
        started = time.monotonic()
        response = super().post(*args, **kwargs)
        latency = time.monotonic() - started
        usage = None
        try:
            payload = response.json()
            if isinstance(payload, dict):
                usage = payload.get("usage")
        except ValueError:
            usage = None
        self.records.append({
            "label": "?",
            "status": response.status_code,
            "latency_s": round(latency, 2),
            "usage": usage,
        })
        return response


def main():
    print("== live DeepSeek evidence run ==")
    for name in ("DEEPSEEK_API_KEY", "TMDB_API_KEY"):
        how = load_secret(name)
        if how is None:
            raise SystemExit("cannot run without " + name)
        print(name + ": loaded from " + how + " (len=" + str(len(os.environ[name])) + ")")

    store = MovieStore(":memory:")
    tmdb = TmdbClient(store=store)
    discovery = DiscoveryService(tmdb, store)
    recorder = RecordingSession()
    ai = AiClient(session=recorder)
    advisor = AiAdvisor(ai, discovery, store)

    print("finding seed movie via TMDB search...")
    results = tmdb.search_movies("Inception")
    seed = None
    for movie in results:
        if movie.get("title") == "Inception" and (movie.get("release_date") or "").startswith("2010"):
            seed = movie
            break
    if seed is None and results:
        seed = results[0]
    if seed is None:
        raise SystemExit("seed search returned nothing")
    details = tmdb.get_movie_details(seed["id"])
    store.add_movie(details)
    store.add_to_watchlist(seed["id"])
    seed_id = seed["id"]
    seed_title = details.get("title") or ""
    seed_year = (details.get("release_date") or "")[:4]
    print("seed: " + seed_title + " (id " + str(seed_id) + ")")

    def label_last(text):
        if recorder.records:
            recorder.records[-1]["label"] = text

    def calls():
        return len(recorder.records)

    print("recommend A...")
    picks_a = advisor.recommend(seed_id, MOOD_A)
    label_last("แนะนำ · โจทย์ A")
    print("recommend B...")
    picks_b = advisor.recommend(seed_id, MOOD_B)
    label_last("แนะนำ · โจทย์ B")

    print("cache check (mood A again)...")
    before = calls()
    again = advisor.recommend(seed_id, MOOD_A)
    cache_calls = calls() - before
    if [m["id"] for m in again] != [m["id"] for m in picks_a]:
        raise SystemExit("cache check mismatch")
    print("cache hit: " + str(cache_calls == 0))

    print("summary 1 (seed)...")
    summary_seed = advisor.summarize(details)
    label_last("สรุป · หนังตั้งต้น")

    print("summary 2 (first pick of A)...")
    pick_id = picks_a[0]["id"]
    pick_details = tmdb.get_movie_details(pick_id)
    summary_pick = advisor.summarize(pick_details)
    label_last("สรุป · " + (pick_details.get("title") or ""))

    now = datetime.now()
    total_in = sum((r["usage"] or {}).get("prompt_tokens") or 0 for r in recorder.records)
    total_out = sum((r["usage"] or {}).get("completion_tokens") or 0 for r in recorder.records)
    cost = total_in / 1e6 * 0.15 + total_out / 1e6 * 0.60

    lines = []
    add = lines.append
    add("# หลักฐานการยิงจริง — DeepSeek (Sprint 4)")
    add("")
    add("**วันเวลาที่รัน:** {:%Y-%m-%d %H:%M} (เวลาท้องถิ่น)".format(now))
    add("**โมเดล:** " + str(ai.model) + " · โหมดคิดปิด · บังคับคำตอบ JSON · เรียกผ่านไคลเอนต์ของโปรเจกต์ (src/ai_client.py)")
    add("**หนังตั้งต้น:** " + seed_title + " (" + (seed_year or "----") + ") · TMDB id " + str(seed_id))
    add("**จำนวนการเรียก AI จริง:** " + str(len(recorder.records)) + " ครั้ง (แนะนำ 2 · สรุป 2) · เรียกโจทย์เดิมซ้ำอีก 1 ครั้งได้ผลจากแคชทันที ไม่เรียก API เพิ่ม")
    add("")
    add("## ผู้ช่วยแนะนำ · โจทย์ A: \"" + MOOD_A + "\"")
    add("")
    add("หนังคล้ายจาก TMDB ถูกส่งให้ AI คัด — ผลลัพธ์ที่ผ่านการตรวจสอบ:")
    add("")
    for index, movie in enumerate(picks_a, 1):
        year = (movie.get("release_date") or "")[:4]
        add(str(index) + ". **" + str(movie.get("title")) + "** (" + (year or "----") + ") — คะแนน " + str(movie.get("vote_average")) + " · TMDB id " + str(movie.get("id")))
        add("   เหตุผลจาก AI: " + str(movie.get("reason")))
    add("")
    add("## ผู้ช่วยแนะนำ · โจทย์ B: \"" + MOOD_B + "\"")
    add("")
    for index, movie in enumerate(picks_b, 1):
        year = (movie.get("release_date") or "")[:4]
        add(str(index) + ". **" + str(movie.get("title")) + "** (" + (year or "----") + ") — คะแนน " + str(movie.get("vote_average")) + " · TMDB id " + str(movie.get("id")))
        add("   เหตุผลจาก AI: " + str(movie.get("reason")))
    add("")
    add("## ตรวจแคช: ยิงโจทย์ A ซ้ำ")
    add("")
    add("ได้ผลชุดเดิม (id ตรงกันทุกเรื่อง) ทันที · ไม่มีการเรียก API เพิ่ม" + (" (ยืนยัน: จำนวนการเรียกคงเดิม)" if cache_calls == 0 else " — พบการเรียกเพิ่ม " + str(cache_calls) + " ครั้ง"))
    add("")
    add("## สรุปภาษาไทย · " + seed_title)
    add("")
    add(str(summary_seed.get("summary")))
    add("")
    add("ทำไมควรดู:")
    for item in summary_seed.get("why", []):
        add("- " + str(item))
    add("")
    add("## สรุปภาษาไทย · " + str(pick_details.get("title")))
    add("")
    add(str(summary_pick.get("summary")))
    add("")
    add("ทำไมควรดู:")
    for item in summary_pick.get("why", []):
        add("- " + str(item))
    add("")
    add("## การใช้งานและค่าใช้จ่าย (วัดจาก response จริง)")
    add("")
    for rec in recorder.records:
        usage = rec["usage"] or {}
        add("- " + rec["label"] + " — HTTP " + str(rec["status"]) + " · " + str(rec["latency_s"]) + " วิ · input " + str(usage.get("prompt_tokens", "-")) + " tokens · output " + str(usage.get("completion_tokens", "-")) + " tokens")
    add("")
    add("**รวมโทเคน:** input " + str(total_in) + " · output " + str(total_out))
    add("**ค่าใช้จ่ายจริง (ราคาปกติ $0.15 input / $0.60 output ต่อล้านโทเคน):** ${:.6f} USD · ช่วงพีก (×2) ≈ ${:.6f} USD".format(cost, cost * 2))
    add("")

    text = "\n".join(lines)
    secrets = [v.strip() for v in (os.environ.get("DEEPSEEK_API_KEY"), os.environ.get("TMDB_API_KEY")) if v]
    if any(s and s in text for s in secrets):
        raise SystemExit("SECRET LEAK detected — evidence not written")
    if re.search(r"sk-[A-Za-z0-9_-]{8,}", text):
        raise SystemExit("key-like string in evidence — not written")

    out_path = HERE / ("live-deepseek-{:%Y-%m-%d}.md".format(now))
    out_path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")
    print("evidence written: " + str(out_path))
    print("calls=" + str(len(recorder.records)) + " in/out=" + str(total_in) + "/" + str(total_out) + " cost_usd={:.6f}".format(cost))


if __name__ == "__main__":
    main()
