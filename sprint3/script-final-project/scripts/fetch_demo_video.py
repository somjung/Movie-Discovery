#!/usr/bin/env python3
"""Download the demo movie for the web player (public-domain / CC files).

Sources come from archive.org (see SOURCES).  archive.org often limits
each connection to a small bandwidth, so the default mode downloads
several byte ranges in parallel and then joins them into the final file.
Every range resumes from its own partial file, a finished download is
skipped, and the size is verified against the expected byte count.

Usage:
    python scripts/fetch_demo_video.py                 # tier 1, 12 streams
    python scripts/fetch_demo_video.py --connections 4 # fewer streams
    python scripts/fetch_demo_video.py --source 2      # fallback source 2
    python scripts/fetch_demo_video.py --source 3      # Big Buck Bunny
    python scripts/fetch_demo_video.py --connections 1 # single stream
    python scripts/fetch_demo_video.py --list          # show all sources
"""

import argparse
import os
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(PROJECT_ROOT, "data", "videos")

DEFAULT_CONNECTIONS = 12
MAX_CONNECTIONS = 16

# Candidate files (tier 1 = first choice).  Sizes were read from the
# servers with a HEAD request; they are used to verify the download.
SOURCES = [
    {
        "tier": 1,
        "file": "night_of_the_living_dead.mp4",
        "url": ("https://archive.org/download/Night.Of.The.Living.Dead_1080p/"
                "NightOfTheLivingDead_DVD5_512kb.mp4"),
        "size": 333938666,
        "license": "Night of the Living Dead (1968) — public domain",
    },
    {
        "tier": 2,
        "file": "night_of_the_living_dead_hd.mp4",
        "url": ("https://archive.org/download/"
                "Night_Of_The_Living_Dead_raw_HD_WS/"
                "NightOfTheLivingDeadWSInternationalPrint.mp4"),
        "size": 817380054,
        "license": "Night of the Living Dead (1968) — public domain (HD)",
    },
    {
        "tier": 3,
        "file": "big_buck_bunny.mp4",
        "url": ("https://archive.org/download/BigBuckBunny_124/Content/"
                "big_buck_bunny_720p_surround.mp4"),
        "size": 61878609,
        "license": "Big Buck Bunny (2008) — CC-BY, Blender Foundation",
    },
]


def human_size(num_bytes):
    """Format a byte count as MB with one decimal."""
    return f"{num_bytes / (1024 * 1024):.1f} MB"


def _report_progress(progress, lock):
    """Print a progress line at ~5% steps (caller already holds the lock)."""
    done = progress["done"]
    if done < progress["next_mark"]:
        return
    total = progress["total"]
    percent = done * 100 // total
    elapsed = max(time.monotonic() - progress["started"], 0.001)
    rate = (done - progress["seeded"]) / elapsed / 1024
    print(f"  ... {percent}% ({human_size(done)} / {human_size(total)}, "
          f"{rate:.0f} KB/s)")
    while progress["next_mark"] <= done:
        progress["next_mark"] += progress["step"]


def _download_range(url, start, end, path, progress, lock, errors):
    """Download bytes ``start``-``end`` into ``path``; resumes partials."""
    expected = end - start + 1
    for attempt in range(1, 4):
        have = os.path.getsize(path) if os.path.exists(path) else 0
        if have > expected:
            os.remove(path)
            have = 0
        if have == expected:
            return
        request = urllib.request.Request(url)
        request.add_header("Range", f"bytes={start + have}-{end}")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 206:
                    raise OSError(
                        f"unexpected status {response.status} for range")
                with open(path, "ab" if have else "wb") as handle:
                    while True:
                        chunk = response.read(256 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
                        with lock:
                            progress["done"] += len(chunk)
                            _report_progress(progress, lock)
        except (urllib.error.URLError, OSError) as exc:
            if attempt == 3:
                with lock:
                    errors.append(f"ช่วง {start}-{end}: {exc}")
                return


def download_parallel(source, connections=DEFAULT_CONNECTIONS):
    """Download in parallel ranges, then join; return path or None."""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    target = os.path.join(VIDEOS_DIR, source["file"])
    expected = source["size"]

    if os.path.exists(target) and os.path.getsize(target) == expected:
        print(f"[ข้าม] มีไฟล์ครบแล้ว: {target} ({human_size(expected)})")
        return target

    chunk = (expected + connections - 1) // connections
    parts = []
    for index in range(connections):
        start = index * chunk
        if start >= expected:
            break
        end = min(start + chunk - 1, expected - 1)
        parts.append((start, end, f"{target}.part{index:02d}"))

    seeded = sum(os.path.getsize(path) for _, _, path in parts
                 if os.path.exists(path))
    if seeded:
        print(f"[ทำต่อ] พบชิ้นส่วนเดิม {human_size(seeded)} — ทำต่อจากเดิม")
    step = max(expected // 20, 1)
    progress = {"done": seeded, "total": expected, "seeded": seeded,
                "started": time.monotonic(), "step": step,
                "next_mark": (seeded // step + 1) * step}
    print(f"[โหลด] {len(parts)} การเชื่อมต่อพร้อมกันจาก archive.org")

    lock = threading.Lock()
    errors = []
    threads = []
    for start, end, path in parts:
        thread = threading.Thread(
            target=_download_range,
            args=(source["url"], start, end, path, progress, lock, errors))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    if errors:
        print("\n[ผิดพลาด] บางช่วงดาวน์โหลดไม่สำเร็จ:")
        for message in errors:
            print(f"  - {message}")
        print("          ชิ้นส่วนที่ได้ถูกเก็บไว้ — รันคำสั่งเดิมเพื่อทำต่อ")
        return None

    print("[ต่อไฟล์] รวมชิ้นส่วนเป็นไฟล์เดียว ...")
    with open(target, "wb") as out:
        for _, _, path in parts:
            with open(path, "rb") as handle:
                shutil.copyfileobj(handle, out)
    final = os.path.getsize(target)
    if final != expected:
        print(f"[ไม่ครบ] ได้ {human_size(final)} แต่คาดหวัง "
              f"{human_size(expected)} — รันซ้ำเพื่อทำต่อ")
        return None
    for _, _, path in parts:
        os.remove(path)
    print(f"[เสร็จ] {target} ({human_size(final)})")
    print(f"        ที่มา: {source['license']}")
    return target


def download_single(source):
    """Download with one stream; return the path or None on failure."""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    target = os.path.join(VIDEOS_DIR, source["file"])
    expected = source["size"]

    if os.path.exists(target) and os.path.getsize(target) == expected:
        print(f"[ข้าม] มีไฟล์ครบแล้ว: {target} ({human_size(expected)})")
        return target

    have = os.path.getsize(target) if os.path.exists(target) else 0
    if have:
        print(f"[ทำต่อ] พบไฟล์บางส่วน {human_size(have)} — ดาวน์โหลดต่อ")

    request = urllib.request.Request(source["url"])
    if have:
        request.add_header("Range", f"bytes={have}-")

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            resuming = response.status == 206 and have > 0
            mode = "ab" if resuming else "wb"
            if have and not resuming:
                print("[เริ่มใหม่] เซิร์ฟเวอร์ไม่ตอบ partial — โหลดทั้งไฟล์")
            received = have if resuming else 0
            mark_step = max(expected // 20, 1)
            next_mark = (received // mark_step + 1) * mark_step
            with open(target, mode) as handle:
                while True:
                    chunk = response.read(256 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
                    received += len(chunk)
                    if received >= next_mark:
                        percent = received * 100 // expected
                        print(f"  ... {percent}% "
                              f"({human_size(received)} / "
                              f"{human_size(expected)})")
                        next_mark += mark_step
    except (urllib.error.URLError, OSError) as exc:
        print(f"\n[ผิดพลาด] ดาวน์โหลดไม่สำเร็จ: {exc}")
        print(f"          ไฟล์บางส่วนอยู่ที่ {target}")
        print("          รันคำสั่งเดิมอีกครั้งเพื่อดาวน์โหลดต่อ")
        return None

    final = os.path.getsize(target)
    if expected and final != expected:
        print(f"[ไม่ครบ] ได้ {human_size(final)} แต่คาดหวัง "
              f"{human_size(expected)} — รันซ้ำเพื่อทำต่อ")
        return None
    print(f"[เสร็จ] {target} ({human_size(final)})")
    print(f"        ที่มา: {source['license']}")
    return target


def main(argv=None):
    """Entry point: parse arguments and download the chosen source."""
    parser = argparse.ArgumentParser(
        description="ดาวน์โหลดไฟล์หนังเดโมสำหรับเว็บเพลเยอร์")
    parser.add_argument("--source", type=int, default=1,
                        choices=[source["tier"] for source in SOURCES],
                        help="เลือกไฟล์ต้นทาง (ค่าเริ่มต้น: 1)")
    parser.add_argument("--connections", type=int, default=DEFAULT_CONNECTIONS,
                        choices=range(1, MAX_CONNECTIONS + 1),
                        help="จำนวนการเชื่อมต่อพร้อมกัน (ค่าเริ่มต้น: 12)")
    parser.add_argument("--list", action="store_true",
                        help="แสดงรายการไฟล์ต้นทางทั้งหมด")
    args = parser.parse_args(argv)

    if args.list:
        for source in SOURCES:
            print(f"  {source['tier']}. {source['file']} — "
                  f"{human_size(source['size'])} — {source['license']}")
        return 0

    source = next(item for item in SOURCES if item["tier"] == args.source)
    print(f"ดาวน์โหลด: {source['license']}")
    print(f"URL: {source['url']}")
    print(f"ปลายทาง: {os.path.join(VIDEOS_DIR, source['file'])}")
    if args.connections == 1:
        result = download_single(source)
    else:
        result = download_parallel(source, args.connections)
    if result is None:
        print("ลองใหม่ หรือใช้ --source 2 / --source 3 เป็นไฟล์สำรอง")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
