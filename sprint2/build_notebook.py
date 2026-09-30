#!/usr/bin/env python3
"""สร้างโน้ตบุ๊กรายงาน Sprint 2 จากไฟล์จริงในโปรเจกต์

โน้ตบุ๊กฝังซอร์สโค้ด "ตามไฟล์จริง" ในโฟลเดอร์ script-final-project/
รายงานกับโค้ดจึงไม่คลาดกัน รันด้วย:

    python build_notebook.py

ผลลัพธ์: Sprint2_MovieDiscovery.ipynb (โฟลเดอร์เดียวกับสคริปต์นี้)
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE / "script-final-project"
OUT = HERE / "Sprint2_MovieDiscovery.ipynb"

# --- narrative (Thai) -------------------------------------------------------

TITLE = """# รายงานผลการดำเนินงาน Sprint 2 (Final Term Project)

## ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)

**รายวิชา:** CP352301 Script Programming (1/2569)
**Sprint 2:** Back-End App Dev (สัปดาห์ที่ 13)
**กำหนดนำเสนอ:** 22–23/9/69
**กำหนดส่งงาน:** 25/9/69

| บทบาท (หมุนเวียนตาม Sprint) | สมาชิกในทีม |
|---|---|
| Planner / Team Leader | [ชื่อนักศึกษา] |
| Coder | นายอเสข ปัญญาวงค์ |
| Debugger / QA | [ชื่อนักศึกษา] |

**Repository:** https://github.com/somjung/Movie-Discovery

---

เนื้อหาของรายงานแบ่งออกเป็น 4 ส่วน ดังนี้

1. **ส่วนที่ 1: บทสรุปโครงการ (Project Recap)** ได้แก่ ภาพรวมของระบบ สถาปัตยกรรม 3 ชั้น และสิ่งที่ Sprint 2 เพิ่มจากรอบก่อน
2. **ส่วนที่ 2: แผนงาน (Plan)** ได้แก่ เป้าหมาย ขอบเขต คำสั่งของระบบ และ Definition of Done ของ Sprint 2
3. **ส่วนที่ 3: การพัฒนา (Execution)** ได้แก่ โค้ดที่ส่งมอบทั้งชุด และสาธิตการทำงานจริงแบบออฟไลน์
4. **ส่วนที่ 4: ผลลัพธ์และการทดสอบ (Result)** ได้แก่ สรุปความก้าวหน้า ตาราง QA บทเรียน และลิงก์ของโปรเจกต์
"""

RECAP = """## ส่วนที่ 1: บทสรุปโครงการ (Project Recap)

### 1. ภาพรวมระบบ

ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)
เป็นแอปพลิเคชันที่เปลี่ยน "ภาพยนตร์ที่ผู้ใช้ชื่นชอบ" ให้กลายเป็น "รายการรับชม" ที่รวบรวมไว้ในที่เดียว
ผู้ใช้ระบุภาพยนตร์ตั้งต้น (Seed Movie) หรือคำค้น ระบบจะดึงข้อมูลจริงจาก TMDB API (The Movie Database)
กรองและจัดอันดับตามเงื่อนไขที่ต้องการ บันทึกผลลงฐานข้อมูล SQLite ส่วนตัว แล้วส่งออกเป็นไฟล์ CSV

จุดเด่นของโครงงาน: ข้อมูลภาพยนตร์ที่คล้ายกันได้มาจาก API โดยตรง
ขณะที่ตรรกะการคัดเลือก การจัดอันดับ การจัดการคลังข้อมูล และการส่งออก เป็นส่วนที่ทีมพัฒนาขึ้นเองทั้งหมด

### 2. สถาปัตยกรรม 3 ชั้น (Separation of Concerns)

Sprint 1 ส่งมอบชั้นนำเสนอ (Presentation Layer) และวางโครงโมดูลทั้งหมดไว้ —
Sprint 2 เปิดใช้งานทั้งสามชั้นครบถ้วน โดยโค้ดแยกหน้าที่ชัดเจนและทิศทางการพึ่งพาชี้ลงล่างเสมอ:

```
        ┌──────────────────────────────────────────────┐
        │  Presentation Layer                          │
        │  cli.py · app.py                             │
        └───────────────────────┬──────────────────────┘
                                │  composes services
        ┌───────────────────────▼──────────────────────┐
        │  Business Logic Layer                        │
        │  discovery.py · watchlist.py                 │
        └───────────────────────┬──────────────────────┘
                                │  constructor injection
        ┌───────────────────────▼──────────────────────┐
        │  Data Access Layer                           │
        │  tmdb_client.py · movie_store.py · exporter.py │
        └──────────────────────────────────────────────┘
              │                  │               │
        TMDB REST API     data/movies.db    data/*.csv
```
*(ภาพที่ 1: โครงสร้าง 3 ชั้นและทิศทางการพึ่งพาของระบบหลัง Sprint 2)*

- **ชั้นนำเสนอ** — CLI รับคำสั่ง ตรวจสอบอินพุต แล้วแสดงผลเป็นข้อความไทย ไม่มีตรรกะการคัดเลือกอยู่ในชั้นนี้
- **ชั้นตรรกะธุรกิจ** — `DiscoveryService` (ค้นหา · กรอง · เรียง · ตัดรายการซ้ำ) และ `WatchlistBuilder` (เพิ่มรายการ · ดึงข้อมูลอัตโนมัติ) ทั้งสองคลาสรับ `TmdbClient` และ `MovieStore` ผ่านพารามิเตอร์ (constructor injection) จึงสลับของจริงกับของจำลองได้อย่างอิสระ
- **ชั้นเข้าถึงข้อมูล** — `TmdbClient` (TMDB + แคช 24 ชั่วโมง) · `MovieStore` (SQLite 6 ตาราง) · `Exporter` (ส่งออก CSV)

### 3. สิ่งที่ Sprint 2 เพิ่มจากรอบก่อน

- เชื่อมต่อ TMDB API จริงผ่านไลบรารี requests พร้อมแคชคำตอบ 24 ชั่วโมงในตาราง `api_cache` — ค้นคำเดิมซ้ำจะไม่ยิงเครือข่ายซ้ำ
- ฐานข้อมูล SQLite 6 ตาราง: `movies` · `similar_links` · `watchlist` · `favorites` · `searches` · `api_cache` — ข้อมูลคงอยู่ข้ามเซสชัน
- คำสั่งชุดเต็ม: `search` · `discover` พร้อมตัวเลือกกรอง/เรียง 5 แบบ · `watchlist add|list|remove|clear` · `favorites` · `export` CSV · `history`
- ข้อความแจ้งข้อผิดพลาดภาษาไทยครบทุกกรณี: ไม่มีคีย์ · คีย์ผิด (401) · ถูกจำกัดอัตรา (429) · ไม่พบข้อมูล (404) · เน็ตหลุด · ข้อมูลตอบกลับผิดรูป
- ชุดทดสอบออฟไลน์ 93 เคส (จาก 40 เคสใน Sprint 1) รันได้โดยไม่ใช้เน็ตและไม่ใช้คีย์
- ขนาดโค้ดชั้น `src/` ขยายจาก 23,803 เป็น 47,343 ไบต์ — พฤติกรรม CLI เดิมจาก Sprint 1 คงอยู่ทั้งหมด
"""

PLAN = """## ส่วนที่ 2: แผนงาน (Plan)

### 2.1 เป้าหมายของ Sprint 2

พัฒนาชั้น Business Logic และ Data Access ให้ทำงานกับข้อมูลจริงจาก TMDB API และจัดเก็บข้อมูลอย่างยั่งยืนในฐานข้อมูล SQLite ประกอบด้วย 5 งานหลัก

1. เชื่อมต่อ TMDB API จริง — จัดการข้อผิดพลาดครบทุกกรณี และแคชผลลัพธ์ไว้ในตาราง `api_cache`
2. ฐานข้อมูล SQLite 6 ตาราง พร้อมใช้งานครบทุกฟังก์ชัน
3. ฟังก์ชันค้นหา (Searching) กรองข้อมูล (Filtering) และเรียงลำดับ (Sorting) ทำงานกับข้อมูลจริง
4. การจัดการ File I/O — ส่งออกรายการรับชมและรายการโปรดเป็นไฟล์ CSV
5. ชุดทดสอบอัตโนมัติแบบ Mock API — ต่อยอด CI เดิมให้เขียวต่อเนื่อง

### 2.2 ขอบเขตและข้อกำหนดคงเดิม

- **ในขอบเขต:** TMDB จริง (ค้นหา · หนังคล้าย · คำแนะนำ) พร้อมแคช · SQLite 6 ตาราง · คำสั่งกรอง/เรียง · ลิสต์เก็บถาวร · CSV · เทสต์แบบ Mock API
- **นอกขอบเขต (ยกไป Sprint 3):** การเชื่อมชั้นนำเสนอรูปแบบเต็มรูปแบบ และการรับมือกรณีขอบเขตเชิงลึกทั่วทั้งระบบ
- **ข้อกำหนดคงเดิม:** พฤติกรรมทั้งหมดจาก Sprint 1 ต้องอยู่ครบ (ข้อความไทย · การตรวจสอบอินพุต · รูปแบบการแสดงผล) และคีย์ API เก็บผ่านตัวแปรสภาพแวดล้อม `TMDB_API_KEY` เท่านั้น — ห้ามปรากฏในโค้ด เอกสาร หรือ commit

### 2.3 คำสั่งของระบบ (ฉบับเต็ม)

| คำสั่ง | พฤติกรรมที่คาดหวัง |
|---|---|
| `search <ชื่อเรื่อง>` | ค้นหาจริงจาก TMDB ผ่านแคช · บันทึกประวัติ · ไม่พบ → แจ้งให้ทราบ |
| `discover <รหัส> [ตัวเลือก]` | รวมหนังคล้าย + คำแนะนำ ตัดซ้ำ กรอง/เรียง/จำกัดจำนวน แล้วบันทึกลงฐานข้อมูล |
| ↳ `--min-rating` · `--min-votes` · `--year` | กรองตามคะแนนขั้นต่ำ · จำนวนโหวตขั้นต่ำ · ช่วงปีที่ฉาย |
| ↳ `--sort` · `--limit` | เรียง rating / votes / year / popularity · จำกัดจำนวน (ค่าเริ่มต้น 10) |
| `watchlist` (add · list · remove · clear) | จัดการรายการรับชม — ไม่เพิ่มซ้ำ · รหัสที่ยังไม่มีในเครื่องดึงจาก TMDB อัตโนมัติ |
| `favorites` (add · list · remove) | จัดการรายการโปรดในฐานข้อมูล |
| `export watchlist` / `export favorites` | เขียนไฟล์ CSV ลงโฟลเดอร์ `data/` แล้วแจ้งที่อยู่ไฟล์ |
| `history [N]` | ประวัติการค้นหาล่าสุด N รายการ (ค่าเริ่มต้น 10) |
| `help` · `quit` / `exit` / `q` / `ออก` | แสดงคำสั่งทั้งหมด · ออกจากโปรแกรมทันที |

### 2.4 Definition of Done (สรุป — ผลการตรวจอยู่ในส่วนที่ 4)

**การทำงานปกติ**

- search กับ TMDB จริง ผลถูกต้องและถูกบันทึกใน `searches` · ค้นซ้ำใช้แคชโดยไม่เรียก API ซ้ำ
- discover ทุกตัวเลือกกรอง/เรียง ผลตรงเงื่อนไข · watchlist และ favorites ทำงานครบ ไม่เพิ่มซ้ำ
- ปิด–เปิดโปรแกรมใหม่ข้อมูลอยู่ครบ · export ได้ไฟล์ CSV ที่เปิดอ่านได้ · history แสดงถูกต้อง

**กรณีผิดพลาดและขอบเขต**

- ไม่มีคีย์ · เน็ตหลุด · 401 · 429 · 404 — แจ้งข้อความอ่านง่าย โปรแกรมไม่หยุดทำงาน
- รหัสผิดรูปแบบ · คำสั่งว่าง · คำสั่งไม่รู้จัก — พฤติกรรมเหมือน Sprint 1 ทุกประการ
- ไฟล์ฐานข้อมูลถูกลบ — โปรแกรมสร้างใหม่ให้อัตโนมัติ ทำงานต่อได้ทันที

**คุณภาพโค้ด**

- flake8 ผ่าน · pytest ผ่านครบทั้งชุดโดยไม่ต้องใช้อินเทอร์เน็ต · CI เขียวต่อเนื่อง
"""

EXEC = """## ส่วนที่ 3: การพัฒนา (Execution)

ลำดับการพัฒนา: ① ออกแบบสคีมา 6 ตารางและสัญญาบริการ → ② เขียนโมดูลชั้นข้อมูลและชั้นตรรกะธุรกิจใหม่ →
③ ขยาย CLI เป็นชุดคำสั่งเต็ม → ④ เขียนชุดทดสอบออฟไลน์แบบฉีดตัวจำลอง → ⑤ ตรวจ flake8 และเตรียม CI

โค้ดที่ส่งมอบทั้งชุดถูกฝังในเซลล์ด้านล่าง **ตามไฟล์จริงในโครงการทุกไบต์** —
โน้ตบุ๊กนี้สร้างด้วยสคริปต์ที่อ่านไฟล์จากโฟลเดอร์โค้ดโดยตรง รายงานกับโค้ดจึงไม่คลาดกัน
จากนั้นเซลล์สาธิตทั้งหมดจะรันจริงแบบ **ออฟไลน์ 100%** ด้วยตัวจำลอง TMDB ชุดเดียวกับชุดทดสอบ
(ไม่ต้องใช้คีย์หรืออินเทอร์เน็ต — รันซ้ำได้ทุกเครื่องและบน CI)
"""

DEMO_HEADER = """### 3.1 สาธิตการทำงานและกรณีขอบเขต (ผลลัพธ์จริงจากการรัน)

เซลล์ถัดไปรันโปรแกรมจริงโดยจำลองอินพุตผู้ใช้ทีละบรรทัด (ไม่ใช่ภาพประกอบ) —
ทุกอย่างออฟไลน์ 100% และผลลัพธ์ที่เห็นคือผลจากการรันจริงในครั้งนี้
"""

RESULT = """## ส่วนที่ 4: ผลลัพธ์และการทดสอบ (Result)

### 4.1 สรุปความก้าวหน้าของงาน (Sprint Progress Summary)

- [x] เชื่อมต่อ TMDB จริงพร้อมแคช 24 ชั่วโมง — พิสูจน์ในเซลล์ "แคชทำงาน": เรียกซ้ำครั้งที่สองไม่ยิงเครือข่ายซ้ำ และเมื่อแคชเก่าเกิน 24 ชั่วโมงระบบจะดึงข้อมูลใหม่ให้อัตโนมัติ
- [x] ฐานข้อมูล SQLite 6 ตารางใช้งานครบ — พิสูจน์ในเซลล์ "ปิด–เปิดโปรแกรมใหม่": รายการยังอยู่ครบ
- [x] คำสั่งชุดเต็มทำงานครบ: `search` · `discover` + ตัวเลือกกรอง/เรียง · `watchlist` · `favorites` · `export` · `history`
- [x] ชุดทดสอบออฟไลน์ 93 เคส ผ่านครบทุกเคส — 42 เคส CLI · 24 เคสการค้นพบ/กรอง/เรียง · 13 เคสคลังข้อมูล · 14 เคสไคลเอนต์ TMDB (ดูผลในเซลล์ pytest ด้านบน)
- [x] flake8 ผ่านทั้งโปรเจกต์ (ผลว่าง = ผ่านทั้งหมด)
- [x] เอกสารประกอบรอบนี้: `sprint2/PLAN.md` และ `sprint2/ARCHITECTURE.md`
- [ ] ส่งมอบงานผ่าน Pull Request บน GitHub (จะเปิด PR เมื่อถึงขั้นส่งมอบตามข้อตกลงของทีม)

### 4.2 ผลการทดสอบกรณีขอบเขต (QA Report)

| รายการทดสอบ | อินพุต | ผลลัพธ์ที่คาดหวัง | ผลการทดสอบจริง | สถานะ |
|---|---|---|---|---|
| ค้นหาภาพยนตร์ปกติ | `search alpha` | พบเรื่องที่ตรงคำค้น | พบ 1 เรื่อง — [101] Alpha Signal (2010) คะแนน 7.8 | PASSED |
| ค้นพบ + กรอง + เรียง | `discover 101 --min-rating 7 --sort rating --limit 3` | เหลือเฉพาะคะแนน 7 ขึ้นไป เรียงมากไปน้อย | 3 เรื่อง: Cobalt Night 8.4 · Emerald Run 8.0 · Alpha Signal 7.8 | PASSED |
| เพิ่มรายการซ้ำ | `watchlist add 101` สองครั้ง | ครั้งที่สองแจ้งว่ามีอยู่แล้ว | "'Alpha Signal' อยู่ในรายการรับชมแล้ว" | PASSED |
| ข้อมูลอยู่ถาวรข้ามเซสชัน | ปิดและเปิดโปรแกรมใหม่ | รายการเดิมอยู่ครบ | เซสชันที่ 2 แสดง 2 เรื่องเดิม ([101] และ [103]) | PASSED |
| ส่งออกไฟล์ CSV | `export watchlist` | ไฟล์มีหัวตารางและข้อมูลครบ | watchlist.csv — หัวตาราง 5 คอลัมน์ + ข้อมูล 2 แถว | PASSED |
| ประวัติการค้นหา | `history` | แสดงคำค้นล่าสุดพร้อมจำนวนผล | 1 รายการ — 'alpha' พบ 1 ผล | PASSED |
| ค้นหาไม่พบผล | `search zzz` | แจ้งไม่พบโดยไม่ล้ม | "ไม่พบภาพยนตร์ที่ตรงกับ 'zzz'" | PASSED |
| รหัสภาพยนตร์ไม่มีจริง (404) | `discover 999` | แจ้งข้อความอ่านง่าย | "ไม่พบรหัสภาพยนตร์ 999 ใน TMDB" | PASSED |
| ตัวเลือกผิดรูปแบบ | `--min-rating abc` · `--sort banana` | แจ้งเตือนแล้วกลับสู่เมนู | "ค่า --min-rating ต้องเป็นตัวเลข" · "--sort ต้องเป็น rating, votes, ..." | PASSED |
| รหัสหนังผิดรูปแบบ | `watchlist add abc` · `-3` · `0` | ปฏิเสธทุกรูปแบบ | "ต้องเป็นตัวเลข" และ "ต้องมากกว่า 0" ตามลำดับ | PASSED |
| ทำงานโดยไม่มีคีย์ TMDB | เปิดโปรแกรมโดยไม่ตั้ง `TMDB_API_KEY` | แจ้งวิธีตั้งค่า · คำสั่งออฟไลน์ยังใช้ได้ | แสดงข้อความวิธีตั้งค่าคีย์ · watchlist/history ทำงานปกติ | PASSED |
| แคชทำงานและหมดอายุ | เรียกคำเดิมซ้ำ (TTL 24 ชม.) | ซ้ำ = ใช้แคช · เกินอายุ = ดึงใหม่ | ยิงเครือข่าย 1 ครั้ง (hit ในครั้งที่ 2) · หลังย้อนเวลา 25 ชม. ดึงใหม่จริง | PASSED |
| อินพุตสิ้นสุด (EOF) | จบอินพุตทันที | ออกอย่างสุภาพ | "[สิ้นสุดอินพุต]" แล้วกล่าวอำลา | PASSED |

### 4.3 สรุปบทเรียน (Retrospective: Wow! & Whoops!)

**Wow! (ส่วนที่ทำได้ดี):**

- ชั้นข้อมูลและตรรกะธุรกิจครบทั้ง 5 งานตามแผน — TMDB จริง + แคช · SQLite 6 ตาราง · ค้นหา/กรอง/เรียง · CSV · ข้อความข้อผิดพลาดภาษาไทย
- ชุดทดสอบ 93 เคสออฟไลน์ 100% (ไม่ใช้เน็ตและไม่ใช้คีย์) — รันซ้ำได้ทุกเครื่องและบน CI โดยไม่มีความไม่แน่นอนของเครือข่าย
- ข้อมูลคงอยู่ข้ามเซสชันจริง (พิสูจน์ในเซลล์ด้านบน) และพฤติกรรม CLI เดิมจาก Sprint 1 ยังอยู่ครบทุกข้อ

**Whoops! (ปัญหาและแนวทางแก้ไข):**

- เมื่อ CLI เปลี่ยนจากข้อมูลตัวอย่างในตัวเป็นบริการจริง ชุดทดสอบเดิมจาก Sprint 1 (40 เคส) ใช้ต่อไม่ได้ทันที — ทุกเคสต้องถูกปรับให้ "ฉีด" ตัวจำลอง (`FakeTmdbClient`) และฐานข้อมูลชั่วคราว (`:memory:`) ผ่านพารามิเตอร์ของ CLI แทน งานรอบนี้จึงรวมการรื้อชุดทดสอบยกชุด ผลลัพธ์คือรูปแบบ injection กลายเป็นมาตรฐานของทั้งโครงการ
- หนี้จาก Sprint 1: รายการรับชมเคยเก็บในหน่วยความจำชั่วคราว ข้อมูลหายเมื่อปิดโปรแกรม — รอบนี้ปิดได้แล้วด้วยฐานข้อมูล SQLite ที่เก็บถาวร

### 4.4 ลิงก์และขั้นตอนถัดไป

- **Repository:** https://github.com/somjung/Movie-Discovery
- **เอกสารประกอบ:** `sprint2/PLAN.md` (แผนงาน) · `sprint2/ARCHITECTURE.md` (สถาปัตยกรรม + แผนภาพคลาส UML)
- **Sprint ถัดไป (Sprint 3 — Full-Stack):** เชื่อมชั้นนำเสนอรูปแบบใหม่ (เว็บแอปพลิเคชัน + เครื่องเล่นวิดีโอ) เข้ากับบริการชุดเดิมของรอบนี้ โดยไม่แก้โค้ด `src/` ที่ส่งมอบแล้ว
"""

FOOTER = """---

*หมายเหตุ: เซลล์สาธิตทั้งหมดในรายงานนี้รันแบบออฟไลน์ 100% — ใช้ตัวจำลอง TMDB ชุดเดียวกับชุดทดสอบ (`tests/fakes.py`) และฐานข้อมูลชั่วคราว จึงไม่ต้องใช้คีย์หรืออินเทอร์เน็ต และรันซ้ำได้ทุกเครื่อง · โน้ตบุ๊กนี้สร้างจากไฟล์โค้ดจริงในโปรเจกต์ด้วยสคริปต์ `build_notebook.py` (อยู่ในโฟลเดอร์เดียวกับโน้ตบุ๊ก) · This product uses the TMDB API but is not endorsed or certified by TMDB.*
"""

# --- runtime cells ----------------------------------------------------------

BOOTSTRAP = '''# เตรียมโครงสร้างโปรเจกต์และย้ายเข้าไปทำงานในโฟลเดอร์
import os
import pathlib
import sys

here = pathlib.Path.cwd()
if (here / "src" / "cli.py").exists():
    ROOT = here  # อยู่ในโฟลเดอร์โปรเจกต์อยู่แล้ว
else:
    ROOT = here / "script-final-project"
    if (ROOT / "src" / "cli.py").exists():
        # รันข้างโฟลเดอร์โปรเจกต์เดิม: ใช้โฟลเดอร์ใหม่ ไม่เขียนทับของเดิม
        ROOT = here / "script-final-project-notebook"
for folder in ("src", "tests", "data"):
    (ROOT / folder).mkdir(parents=True, exist_ok=True)
os.chdir(ROOT)
ROOT = pathlib.Path.cwd()
for path in (ROOT, ROOT / "tests"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
print("working directory:", ROOT)
print("python:", sys.version.split()[0])
'''

PIP = '''# ติดตั้งไลบรารีที่ใช้รันและทดสอบ (ถ้ามีอยู่แล้วระบบจะข้ามให้)
%pip install -q pytest flake8 requests
import pytest
print("pytest", pytest.__version__)
'''

DEMO = '''# สาธิตการใช้งานจริง (ออฟไลน์ 100%): จำลองผู้ใช้พิมพ์คำสั่งทีละบรรทัด
import pathlib
import tempfile

from fakes import FakeTmdbClient
from src.cli import CLI
from src.movie_store import MovieStore


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


work = pathlib.Path(tempfile.mkdtemp(prefix="sprint2-demo-"))
CLI(input_func=scripted(["search alpha",
                         "discover 101 --min-rating 7 --sort rating --limit 3",
                         "watchlist add 101",
                         "watchlist add 101",
                         "watchlist add 103",
                         "watchlist list",
                         "favorites add 103",
                         "favorites list",
                         "export watchlist",
                         "history",
                         "quit"]),
    output_func=print,
    client=FakeTmdbClient(),
    store=MovieStore(str(work / "movies.db")),
    data_dir=str(work)).run()

print()
print("--- เนื้อหาไฟล์ watchlist.csv ---")
print((work / "watchlist.csv").read_text(encoding="utf-8"))
'''

EDGE = '''# ทดลองกรณีขอบเขตตาม Definition of Done (ผลลัพธ์จริงจากโปรแกรม)
from fakes import FakeTmdbClient
from src.cli import CLI
from src.movie_store import MovieStore

work2 = pathlib.Path(tempfile.mkdtemp(prefix="sprint2-edge-"))
scenarios = [
    ("1) ค้นหาไม่พบผล", ["search zzz", "quit"]),
    ("2) รหัสภาพยนตร์ไม่มีจริง (404)", ["discover 999", "quit"]),
    ("3) ตัวเลือกผิดรูปแบบ", ["discover 101 --min-rating abc", "quit"]),
    ("4) วิธีเรียงที่ไม่รองรับ", ["discover 101 --sort banana", "quit"]),
    ("5) รหัสหนังผิดรูปแบบ", ["watchlist add abc", "watchlist add -3",
                              "watchlist add 0", "quit"]),
    ("6) อินพุตสิ้นสุด (EOF)", []),
]
for title, lines in scenarios:
    print("=" * 62)
    print(title)
    print("-" * 62)
    CLI(input_func=scripted(lines), output_func=print,
        client=FakeTmdbClient(), store=MovieStore(":memory:"),
        data_dir=str(work2)).run()
    print()
'''

KEYLESS = '''# โหมดไม่มีคีย์ TMDB: โปรแกรมต้องไม่ล้ม และคำสั่งออฟไลน์ยังใช้ได้
import os

os.environ.pop("TMDB_API_KEY", None)
print("=" * 62)
print("โหมดไม่มีคีย์ TMDB")
print("-" * 62)
CLI(input_func=scripted(["search alpha", "watchlist list", "history", "quit"]),
    output_func=print, client=None, store=MovieStore(":memory:"),
    data_dir=str(work2)).run()
'''

CACHE = '''# แคชของ TmdbClient: คำตอบเดิมภายใน 24 ชั่วโมงต้องไม่ยิงเครือข่ายซ้ำ
from fakes import FakeResponse
from src.sample_data import SAMPLE_MOVIES
from src.tmdb_client import TmdbClient


class CountingSession:
    """ตัวจำลอง requests.Session: นับจำนวนการยิงเครือข่ายจริง"""

    def __init__(self):
        self.calls = 0

    def get(self, url, params=None, timeout=None):
        self.calls += 1
        return FakeResponse(200, {"results": [SAMPLE_MOVIES[0]]})


work3 = pathlib.Path(tempfile.mkdtemp(prefix="sprint2-cache-"))
store3 = MovieStore(str(work3 / "movies.db"))
session = CountingSession()

client = TmdbClient(api_key="demo-key", session=session, store=store3)
client.search_movies("alpha")
print("เรียกครั้งที่ 1: ยิงเครือข่ายทั้งหมด", session.calls, "ครั้ง |",
      "misses:", client.cache_misses, "hits:", client.cache_hits)

client.search_movies("alpha")
print("เรียกครั้งที่ 2: ยิงเครือข่ายทั้งหมด", session.calls, "ครั้ง |",
      "misses:", client.cache_misses, "hits:", client.cache_hits)

# จำลองว่าผ่านมา 25 ชั่วโมง: ย้อนเวลาแถวแคชในฐานข้อมูล (TTL = 24 ชม.)
with store3.conn:
    store3.conn.execute(
        "UPDATE api_cache SET fetched_at = datetime('now', '-25 hours')")
refreshed = TmdbClient(api_key="demo-key", session=session, store=store3)
refreshed.search_movies("alpha")
print("หลังแคชเก่าเกิน 24 ชม.: ยิงเครือข่ายทั้งหมด", session.calls, "ครั้ง |",
      "misses:", refreshed.cache_misses, "hits:", refreshed.cache_hits)
'''

PERSIST = '''# ข้อมูลอยู่ถาวรข้ามเซสชัน: ปิดโปรแกรมแล้วเปิดใหม่ ข้อมูลต้องอยู่ครบ
work4 = pathlib.Path(tempfile.mkdtemp(prefix="sprint2-persist-"))
db4 = str(work4 / "movies.db")

print("=" * 62)
print("เซสชันที่ 1 — เพิ่มรายการแล้วปิดโปรแกรม")
print("-" * 62)
store_a = MovieStore(db4)
CLI(input_func=scripted(["watchlist add 101", "watchlist add 103", "quit"]),
    output_func=print, client=FakeTmdbClient(), store=store_a,
    data_dir=str(work4)).run()
store_a.close()

print()
print("=" * 62)
print("เซสชันที่ 2 — เปิดโปรแกรมใหม่ ข้อมูลต้องอยู่ครบ")
print("-" * 62)
CLI(input_func=scripted(["watchlist list", "quit"]),
    output_func=print, client=FakeTmdbClient(), store=MovieStore(db4),
    data_dir=str(work4)).run()
'''

PYTEST = '''# รันชุดทดสอบอัตโนมัติทั้ง 93 เคส (จำลองอินพุต/เครือข่าย ไม่ต้องใช้คีย์จริง)
import sys
!{sys.executable} -m pytest -q
'''

FLAKE8 = '''# ตรวจสอบมาตรฐานโค้ด (PEP 8)
import sys
!{sys.executable} -m flake8 src tests
print("ผลตรวจ flake8 ด้านบน (ว่าง = ผ่านทั้งหมด)")
'''

TREE = '''# ไฟล์ทั้งหมดที่สร้างขึ้นจากรายงานนี้
import pathlib

skip = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
for path in sorted(pathlib.Path(".").rglob("*")):
    if path.is_dir():
        continue
    if any(part in skip for part in path.parts):
        continue
    print("  " + path.relative_to(".").as_posix())
'''

# --- files embedded into the notebook (kept in sync with the repo) ----------

EMBED = [
    "requirements.txt",
    "setup.cfg",
    ".env.example",
    "src/__init__.py",
    "src/config.py",
    "src/sample_data.py",
    "src/tmdb_client.py",
    "src/movie_store.py",
    "src/discovery.py",
    "src/watchlist.py",
    "src/exporter.py",
    "src/cli.py",
    "src/app.py",
    "tests/conftest.py",
    "tests/fakes.py",
    "tests/test_tmdb_client.py",
    "tests/test_movie_store.py",
    "tests/test_discovery_flow.py",
    "tests/test_cli.py",
]


def read_source(rel):
    """อ่านไฟล์จริงจากโฟลเดอร์โค้ด (บรรทัดใหม่เป็น LF เสมอ)"""
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
        md(RECAP),
        md(PLAN),
        md(EXEC),
        code(BOOTSTRAP),
        code(PIP),
    ]
    for rel in EMBED:
        cells.append(code(f"%%writefile {rel}\n" + read_source(rel)))
    cells += [
        md(DEMO_HEADER),
        code(DEMO),
        code(EDGE),
        code(KEYLESS),
        code(CACHE),
        code(PERSIST),
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
