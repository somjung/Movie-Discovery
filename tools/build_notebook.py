#!/usr/bin/env python3
"""Rebuild notebooks/Sprint1_MovieDiscovery.ipynb from the repository files.

The Sprint 1 submission notebook embeds the delivered source exactly as it
exists in this repository, so the notebook and the code can never drift
apart. Run from anywhere with:

    python tools/build_notebook.py

Output: notebooks/Sprint1_MovieDiscovery.ipynb
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "Sprint1_MovieDiscovery.ipynb"

# --- narrative (Thai) -----------------------------------------------------

TITLE = """# รายงานผลการดำเนินงาน Sprint 1 — Final Term Project

## ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)

**รายวิชา:** CP352301 Script Programming (1/2569) · **Sprint 1:** Front-End App Dev (สัปดาห์ที่ 12)
**นำเสนอ:** 15–16/9/69 · **ส่งงาน:** 18/9/69

| บทบาท (หมุนเวียนตาม Sprint) | สมาชิกในทีม |
|---|---|
| Planner / Team Leader | [ชื่อนักศึกษา] |
| Coder | [ชื่อนักศึกษา] |
| Debugger / QA | [ชื่อนักศึกษา] |

**Repository / Pull Request:** _(จะเพิ่มลิงก์เมื่อสร้าง Pull Request บน GitHub)_

---

โน้ตบุ๊กนี้เป็นรายงาน Sprint 1 ตามวงรอบ **Plan → Execution → Review** รันได้ครบวงจรทันที
โดยไม่ต้องใช้คีย์ API หรืออินเทอร์เน็ต (สาธิตด้วยข้อมูลตัวอย่างในตัวโปรแกรม)

**โครงสร้างรายงาน:** ส่วนที่ 1 แผนงาน · ส่วนที่ 2 การพัฒนา · ส่วนที่ 3 ผลลัพธ์และการทดสอบ
"""

PLAN = """## ส่วนที่ 1 — แผนงาน (Plan)

### 1.1 เป้าหมายและขอบเขตของ Sprint 1

**เป้าหมาย:** พัฒนาส่วนปฏิสัมพันธ์กับผู้ใช้ (Presentation Layer) ของโปรแกรม — ข้อความต้อนรับ ·
เมนูคำสั่ง · การรับและแปลงอินพุต (`.strip().lower()`) · การตรวจสอบความถูกต้องของข้อมูลนำเข้า
โดยโปรแกรมต้องไม่หยุดทำงานเมื่อผู้ใช้ป้อนข้อมูลผิดพลาด

**ขอบเขต Sprint 1:** CLI แบบพิมพ์คำสั่ง · เมนู · การตรวจสอบอินพุต · การจัดการข้อผิดพลาด · ชุดทดสอบอัตโนมัติ

**นอกขอบเขต (Sprint 2 เป็นต้นไป):** TMDB API จริง · ฐานข้อมูล SQLite · อัลกอริทึมค้นหา/กรอง/เรียงลำดับ · ส่งออก CSV
(คำสั่ง search / discover สาธิตด้วยข้อมูลตัวอย่างในตัวโปรแกรม)

### 1.2 คำสั่งของระบบ

| คำสั่ง | อินพุต | พฤติกรรมที่คาดหวัง |
|---|---|---|
| `search <ชื่อเรื่อง>` | ข้อความ | ค้นหาจากข้อมูลตัวอย่าง · ไม่พบ → ข้อความแจ้ง |
| `discover <รหัส>` | จำนวนเต็ม > 0 | แสดงภาพยนตร์ที่คล้ายกัน เรียงตามคะแนน |
| `watchlist add <รหัส>` | จำนวนเต็ม > 0 | เพิ่มเข้ารายการรับชม (ป้องกันเพิ่มซ้ำ) |
| `watchlist list` / `clear` | — | แสดง / ล้างรายการรับชม |
| `help` | — | แสดงคำสั่งทั้งหมด |
| `quit` / `exit` / `q` / `ออก` | — | ออกทันที (ไม่สนใจตัวพิมพ์เล็ก–ใหญ่/ช่องว่าง) |

### 1.3 Definition of Done (ผลตรวจครบในส่วนที่ 3)

- [ ] พิมพ์ `quit` / `QUIT` / `Quit` / `  quit  ` → ออกทันทีพร้อมข้อความอำลา
- [ ] คำสั่งไม่รู้จัก → แจ้งเตือนและกลับสู่เมนู (โปรแกรมไม่หยุดทำงาน)
- [ ] บรรทัดว่างหรือช่องว่างล้วน → แจ้งเตือน "กรุณาพิมพ์คำสั่ง"
- [ ] รหัสภาพยนตร์ที่ไม่ใช่ตัวเลข (`abc`) → แจ้งเตือน ไม่ crash (try / except ValueError)
- [ ] รหัสภาพยนตร์ติดลบหรือศูนย์ → ปฏิเสธพร้อมข้อความ
- [ ] อินพุตสิ้นสุด (EOF) หรือ Ctrl+C → ออกจากโปรแกรมอย่างสุภาพ
- [ ] โค้ดผ่าน flake8 และมี docstring ครบทุกเมธอด
"""

EXEC = """## ส่วนที่ 2 — การพัฒนา (Execution)

เซลล์ด้านล่างสร้างโครงสร้างโปรเจกต์ตาม `PLAN.md` เขียนโค้ดที่ส่งมอบ แล้วสาธิตการทำงานจริง
ด้วยการจำลองอินพุต — ผลลัพธ์ทั้งหมดเป็นผลรันจริงจากโค้ดด้านบน
"""

RESULT = """## ส่วนที่ 3 — ผลลัพธ์และการทดสอบ (Result & Review)

### 3.1 สรุปความก้าวหน้าของงาน (Sprint Progress Summary)

- [x] ออกแบบโครงสร้างระบบและนิยาม Definition of Done ใน `PLAN.md`
- [x] พัฒนาชุดคำสั่งหลัก: `display_welcome_message` · `get_command_input` · เมนูและตัวจัดการคำสั่ง · ลูป `run`
- [x] ดักจับข้อผิดพลาดด้วย `try / except` (อินพุตผิดรูป · EOF · Ctrl+C)
- [x] ทดสอบอัตโนมัติ 20 เคสของ CLI (ผ่านทั้งหมด — เซลล์ pytest ด้านบน) + ทดสอบด้วยเซสชันสคริปต์
- [ ] ส่งมอบผ่าน Pull Request บน GitHub _(รอลิงก์ repository จากทีม)_

### 3.2 ผลการทดสอบกรณีขอบเขต (QA Report)

| รายการทดสอบ | อินพุต | ผลลัพธ์ที่คาดหวัง | ผลการทดสอบจริง | สถานะ |
|---|---|---|---|---|
| ออกจากโปรแกรม (ตัวพิมพ์ใหญ่) | `QUIT` | อำลาและหยุดทำงาน | แสดงข้อความอำลาและหลุดจากลูป | PASSED |
| ออกจากโปรแกรม (มีช่องว่างรอบ) | `   Quit   ` | อำลาและหยุดทำงาน | ตัดช่องว่างก่อนประมวลผล อำลาถูกต้อง | PASSED |
| คำสั่งไม่รู้จัก | `asdf` | แจ้งเตือน กลับเมนู | แจ้งเตือน "ไม่รู้จักคำสั่ง..." และกลับเมนู | PASSED |
| บรรทัดว่าง | (Enter เปล่า) | แจ้งเตือน ไม่ crash | แจ้งเตือน "กรุณาพิมพ์คำสั่ง..." | PASSED |
| รหัสไม่ใช่ตัวเลข | `discover abc` | แจ้งเตือน ไม่ crash | "รหัสภาพยนตร์ต้องเป็นตัวเลข..." | PASSED |
| รหัสติดลบ / ศูนย์ | `discover -3`, `0` | ปฏิเสธพร้อมข้อความ | "รหัสภาพยนตร์ต้องมากกว่า 0..." | PASSED |
| ค้นหาปกติ | `search alpha` | พบภาพยนตร์ | พบ 1 เรื่อง (Alpha Signal) | PASSED |
| ป้องกันเพิ่มซ้ำ | `watchlist add 101` ×2 | เพิ่มครั้งเดียว | ครั้งที่สองแจ้ง "อยู่ในรายการรับชมแล้ว" | PASSED |
| อินพุตสิ้นสุด | EOF | ออกอย่างสุภาพ | แสดง "[สิ้นสุดอินพุต]" + ข้อความอำลา | PASSED |

### 3.3 สรุปบทเรียน (Retrospective: Wow! & Whoops!)

**Wow! (ส่วนที่ทำได้ดี):** แยกส่วนนำเสนอ (CLI) ออกจากส่วนอื่นอย่างชัดเจน ทำให้ทดสอบง่าย ·
การตรวจสอบอินพุตครอบคลุมทุกกรณีใน Definition of Done · มีชุดทดสอบอัตโนมัติ 20 เคส
ที่จำลองอินพุตได้จริง ทำให้ทุก DoD พิสูจน์ซ้ำได้ด้วยคำสั่งเดียว

**Whoops! (ปัญหาและแนวทางแก้ไข):** เดิม CLI ถูกออกแบบเป็นคำสั่งแบบครั้งเดียว (argparse)
แต่สเปก Sprint 1 ต้องการเมนูแบบโต้ตอบพร้อมตรวจสอบอินพุต — จึงรีแฟกเตอร์มาเป็นคลาส `CLI`
ที่แยกส่วนนำเสนอชัดเจน · รายการรับชมยังเป็นข้อมูลชั่วคราวในหน่วยความจำ (ปิดโปรแกรมแล้วหาย)
— กำหนดแนวทางแก้เป็นฐานข้อมูล SQLite ใน Sprint 3

### 3.4 ลิงก์และขั้นตอนถัดไป

- **Repository / Pull Request:** _(จะเพิ่มเมื่อสร้างบน GitHub)_
- **Sprint 2 (Back-End):** เชื่อมต่อ TMDB API จริง · SQLite · ค้นหา/กรอง/เรียงลำดับ · File I/O
"""

FOOTER = """---

*ข้อมูลภาพยนตร์ใน Sprint 1 เป็นข้อมูลตัวอย่างสำหรับสาธิตส่วนติดต่อผู้ใช้ — การเชื่อมต่อ TMDB API จริงเริ่มใน Sprint 2
(เมื่อเชื่อมแล้วจะแสดงข้อความ "This product uses the TMDB API but is not endorsed or certified by TMDB." ในโปรแกรมและเอกสาร)*

*จัดทำเพื่อส่งงาน Sprint 1 รายวิชา CP352301 Script Programming (1/2569) — เซลล์ทั้งหมดรันจริงครบวงจร กด "Run all" เพื่อทำซ้ำได้ทันที*
"""

# --- runtime cells --------------------------------------------------------

BOOTSTRAP = '''# เตรียมโครงสร้างโปรเจกต์และย้ายเข้าไปทำงานในโฟลเดอร์
import os
import pathlib
import sys

here = pathlib.Path.cwd()
ROOT = here if here.name == "script-final-project" else here / "script-final-project"
for folder in ("src", "tests", "data", "notebooks"):
    (ROOT / folder).mkdir(parents=True, exist_ok=True)
os.chdir(ROOT)
ROOT = pathlib.Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
print("working directory:", ROOT)
print("python:", sys.version.split()[0])
'''

PIP = '''# ติดตั้งไลบรารีที่ใช้ทดสอบ (มีอยู่แล้วในเครื่องจะข้ามทันที)
%pip install -q pytest flake8
import pytest
print("pytest", pytest.__version__)
'''

DEMO = '''# สาธิตเซสชันการใช้งานจริง: จำลองอินพุตเหมือนผู้ใช้พิมพ์ทีละบรรทัด (ผลรันจริง)
from src.cli import CLI


def scripted(lines):
    """ฟังก์ชันอินพุตจำลอง: คืนค่าทีละบรรทัด แล้วส่ง EOF เมื่ออินพุตหมด"""
    queue = list(lines)

    def feed(prompt=""):
        if not queue:
            raise EOFError
        value = queue.pop(0)
        print(prompt + value)  # แสดงบรรทัดที่ "พิมพ์" เพื่อให้อ่าน transcript ได้
        return value

    return feed


demo_lines = ["search alpha", "discover 103",
              "watchlist add 101", "watchlist list", "quit"]
CLI(input_func=scripted(demo_lines), output_func=print).run()
'''

EDGE = '''# จำลองกรณีขอบเขตตาม Definition of Done (ผลรันจริงจากระบบ)
from src.cli import CLI


def scripted(lines):
    """ฟังก์ชันอินพุตจำลอง (เหมือนเซลล์ก่อนหน้า)"""
    queue = list(lines)

    def feed(prompt=""):
        if not queue:
            raise EOFError
        value = queue.pop(0)
        print(prompt + value)
        return value

    return feed


scenarios = [
    ("1) quit ตัวพิมพ์ใหญ่", ["QUIT"]),
    ("2) quit มีช่องว่างรอบ", ["   Quit   "]),
    ("3) บรรทัดว่าง", ["", "quit"]),
    ("4) คำสั่งไม่รู้จัก", ["asdf", "quit"]),
    ("5) รหัสไม่ใช่ตัวเลข", ["discover abc", "quit"]),
    ("6) รหัสติดลบ / ศูนย์", ["discover -3", "discover 0", "quit"]),
    ("7) อินพุตสิ้นสุด (EOF)", []),
]
for title, lines in scenarios:
    print("=" * 62)
    print(title)
    print("-" * 62)
    CLI(input_func=scripted(lines), output_func=print).run()
'''

PYTEST = '''# รันชุดทดสอบอัตโนมัติของ CLI (จำลองอินพุต ไม่ต้องใช้ terminal จริง)
import sys
!{sys.executable} -m pytest -q
'''

FLAKE8 = '''# ตรวจสอบมาตรฐานโค้ด (PEP 8)
import sys
!{sys.executable} -m flake8 src tests
print("ผลตรวจ flake8 ด้านบน (ว่าง = ผ่านทั้งหมด)")
'''

TREE = '''# ไฟล์ทั้งหมดที่สร้างขึ้นในรอบนี้
import pathlib

skip = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
for path in sorted(pathlib.Path(".").rglob("*")):
    if path.is_dir():
        continue
    if any(part in skip for part in path.parts):
        continue
    print("  " + path.relative_to(".").as_posix())
'''

# --- files embedded into the notebook (kept in sync with the repo) --------

EMBED = [
    "requirements.txt",
    "setup.cfg",
    "PLAN.md",
    "src/__init__.py",
    "src/sample_data.py",
    "src/cli.py",
    "src/app.py",
    "tests/conftest.py",
    "tests/test_cli.py",
]


def read_source(rel):
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"missing source file: {path}")
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.endswith("\n"):
        text += "\n"
    return text


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": source}


def build():
    cells = [
        md(TITLE),
        md(PLAN),
        md(EXEC),
        code(BOOTSTRAP),
        code(PIP),
    ]
    for rel in EMBED:
        cells.append(code(f"%%writefile {rel}\n" + read_source(rel)))
    cells += [
        code(DEMO),
        code(EDGE),
        code(PYTEST),
        code(FLAKE8),
        code(TREE),
        md(RESULT),
        md(FOOTER),
    ]
    for index, cell in enumerate(cells, start=1):
        cell["id"] = f"cell{index:02d}"
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return notebook


def main():
    notebook = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(notebook, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    n_code = sum(1 for c in notebook["cells"] if c["cell_type"] == "code")
    n_md = len(notebook["cells"]) - n_code
    print(f"wrote {OUT}")
    print(f"cells: {len(notebook['cells'])} ({n_md} markdown, {n_code} code)")
    print(f"embedded files: {len(EMBED)}")


if __name__ == "__main__":
    main()
