#!/usr/bin/env python3
"""สร้างโน้ตบุ๊กรายงาน Sprint 3 จากไฟล์จริงในโปรเจกต์

โน้ตบุ๊กฝังซอร์สโค้ด "ตามไฟล์จริง" ในโฟลเดอร์ script-final-project/
รายงานกับโค้ดจึงไม่คลาดกัน รันด้วย:

    python build_notebook.py

ผลลัพธ์: Sprint3_MovieDiscovery.ipynb (โฟลเดอร์เดียวกับสคริปต์นี้)
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE / "script-final-project"
OUT = HERE / "Sprint3_MovieDiscovery.ipynb"

# --- narrative (Thai) -------------------------------------------------------

TITLE = """# รายงานผลการดำเนินงาน Sprint 3 (Final Term Project)

## ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)

**รายวิชา:** CP352301 Script Programming (1/2569)
**Sprint 3:** Full-Stack App Dev — Web App (สัปดาห์ที่ 14)
**กำหนดนำเสนอ:** 29–30/9/69
**กำหนดส่งงาน:** 2/10/69

| บทบาท (หมุนเวียนตาม Sprint) | สมาชิกในทีม |
|---|---|
| Planner / Team Leader | นางสาวพลอยชมพู วงศ์กีรติกุล |
| Coder | นายอเสข ปัญญาวงค์ |
| Debugger / QA | นายนวมินทร์ คำจันทร์ |

**Repository:** https://github.com/somjung/Movie-Discovery

---

เนื้อหาของรายงานแบ่งออกเป็น 4 ส่วน ดังนี้

1. **ส่วนที่ 1: บทสรุปโครงการ (Project Recap)** ได้แก่ ภาพรวมของระบบ สถาปัตยกรรม และสิ่งที่ Sprint 3 เพิ่มจากรอบก่อน
2. **ส่วนที่ 2: แผนงาน (Plan)** ได้แก่ เป้าหมาย ขอบเขต หน้าจอ/เส้นทาง และกรณีขอบเขต
3. **ส่วนที่ 3: การพัฒนา (Execution)** ได้แก่ โค้ดที่ส่งมอบทั้งชุด และสาธิตการทำงานจริงแบบออฟไลน์
4. **ส่วนที่ 4: ผลลัพธ์และการทดสอบ (Result)** ได้แก่ สรุปความก้าวหน้า ตาราง QA บทเรียน และลิงก์ของโปรเจกต์
"""

RECAP = """## ส่วนที่ 1: บทสรุปโครงการ (Project Recap)

### 1. ภาพรวมระบบ

ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)
เป็นแอปพลิเคชันที่เปลี่ยน "ภาพยนตร์ที่ผู้ใช้ชื่นชอบ" ให้กลายเป็น "รายการรับชม" ที่รวบรวมไว้ในที่เดียว
ผู้ใช้ระบุภาพยนตร์ตั้งต้น (Seed Movie) หรือคำค้น ระบบดึงข้อมูลจริงจาก TMDB API (The Movie Database)
กรองและจัดอันดับตามเงื่อนไขที่ต้องการ บันทึกผลลงฐานข้อมูล SQLite ส่วนตัว แล้วส่งออกเป็นไฟล์ CSV

Sprint 3 เป็นรอบ Full-Stack ตามคู่มือรายวิชา: เชื่อมชั้นนำเสนอเข้ากับระบบหลังบ้านให้สมบูรณ์
จัดการสถานะ (State) และความสอดคล้องของข้อมูลทั่วระบบ และรับมือกรณีขอบเขตครบถ้วน —
รอบนี้เพิ่ม **เว็บแอปพลิเคชัน** เป็นชั้นนำเสนอใหม่ (คู่มืออนุญาต CLI หรือ GUI)

### 2. สถาปัตยกรรม 3 ชั้นหลังรอบนี้

โครง 3 ชั้นของ Sprint 1–2 คงอยู่ทั้งหมด — Sprint 3 เปลี่ยนเฉพาะชั้นนำเสนอ:

```
        ┌──────────────────────────────────────────────┐
        │  Presentation Layer                          │
        │  web/ (Flask)  ·  cli.py · app.py            │
        └───────────────────────┬──────────────────────┘
                                │  ใช้บริการชุดเดียวกัน
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
*(ภาพที่ 1: โครงสร้าง 3 ชั้นและทิศทางการพึ่งพาของระบบหลัง Sprint 3)*

- เว็บนำเข้า (import) โมดูลเดิมจาก `src/` โดยไม่คัดลอกตรรกะซ้ำ — และไม่แก้โค้ด `src/` ที่ส่งมอบแล้ว
- เว็บกับ CLI ใช้บริการและฐานข้อมูลชุดเดียวกัน (`data/movies.db`) — เพิ่มรายการจากฝั่งหนึ่ง อีกฝั่งเห็นทันที
- การเชื่อมต่อ SQLite เปิด–ปิดใหม่ต่อหนึ่งคำขอ เพราะเซิร์ฟเวอร์เว็บทำงานหลาย thread

### 3. สิ่งที่ Sprint 3 เพิ่มจากรอบก่อน

- เว็บแอปพลิเคชัน (Flask) ครบทุกหน้าจอ: หน้าแรก · ค้นหา · รายละเอียดหนัง + หนังคล้ายพร้อมตัวกรอง · รายการรับชม · รายการโปรด (ป้าย ★ ไขว้ลิสต์) · ประวัติ · ดาวน์โหลด CSV · หน้าข้อผิดพลาดแบบสุภาพ (404 · TMDB ล่ม 502 · ฐานข้อมูลเสีย)
- การจัดการ State และความสอดคล้องของข้อมูล: จำนวนรายการบนแถบนำทางมาจากฐานข้อมูลจริง อัปเดตทันทีหลังทุกการเพิ่ม/ลบ · ไฟล์ CSV ตรงกับลิสต์ปัจจุบันเสมอ
- โค้ด src/ ทั้ง 10 โมดูลเหมือนรอบ Sprint 2 ทุกไบต์ (ตรวจเทียบแล้ว) — เพิ่มเฉพาะ web/ และชุดทดสอบเว็บ
- ชุดทดสอบ 133 เคส (เดิม 93 + ใหม่ 40 สำหรับเว็บ) ออฟไลน์ 100% · flake8 ผ่านทั้งโปรเจกต์รวม web/
"""

PLAN = """## ส่วนที่ 2: แผนงาน (Plan)

### 2.1 เป้าหมายของ Sprint 3

คู่มือรายวิชากำหนด Sprint 3 เป็น Full-Stack App Dev: เชื่อมต่อ Front-End และ Back-End ให้สมบูรณ์ ·
จัดการ State · ความสอดคล้องของข้อมูล · การรับมือกรณีขอบเขต (Edge Cases) รอบนี้จึง:

1. สร้างส่วนปฏิสัมพันธ์กับผู้ใช้ใหม่เป็นเว็บแอปพลิเคชัน เชื่อมกับ Business Logic และ Data Access เดิมทั้งหมด
2. จัดการ State และความสอดคล้องของข้อมูลในมุมมองเว็บ (จำนวนรายการ · ป้ายไขว้ลิสต์ · ข้อมูลชุดเดียวกับ CLI)
3. รับมือ Edge Cases ครบทั้งระบบ: คีย์หาย · เน็ตหลุด · ฐานข้อมูลเสีย · URL ผิด
4. ต่อยอดชุดทดสอบอัตโนมัติ (Flask test client + ตัวจำลองเดิม) และคง CI ให้เขียวต่อเนื่อง

### 2.2 ขอบเขต

- **ในขอบเขต:** เว็บครบทุกหน้าจอหลัก · ปุ่มเพิ่ม/ลบ/เคลียร์จากหน้าเว็บ · ดาวน์โหลด CSV · ป้าย ★ · กรณีขอบเขตตามหัวข้อ 2.4 · เทสต์ใหม่ + CI
- **นอกขอบเขต:** การพัฒนา CLI เพิ่มเติม (หยุดไว้ที่ Sprint 2 — โค้ดคงอยู่ ไม่ลบ) · ฟีเจอร์ค้นหาเชิงลึก (ประเภท/นักแสดง · ช่องทางรับชม) ยกไป Sprint สุดท้าย · การติดตั้งบนคลาวด์ · ระบบบัญชีผู้ใช้
- **ข้อกำหนด:** คีย์ API เก็บผ่านตัวแปรสภาพแวดล้อม `TMDB_API_KEY` เท่านั้น

### 2.3 หน้าจอและเส้นทาง (Route Specification)

| เส้นทาง | หน้าที่ |
|---|---|
| `GET /` | หน้าแรก — ช่องค้นหา · ลิงก์ทุกหน้า · จำนวนรายการบนแถบนำทาง · แบนเนอร์เมื่อไม่มีคีย์ |
| `GET /search?q=` | ผลการค้นหา (การ์ดหนัง) · บันทึกประวัติอัตโนมัติ |
| `GET /movie/<id>` | รายละเอียดหนัง + หนังคล้ายพร้อมตัวกรอง (คะแนน · โหวต · ปี · เรียง · จำนวน) + ปุ่มเพิ่มสองลิสต์ |
| `POST /watchlist/add/<id>` · `/remove/<id>` · `/clear` | จัดการรายการรับชมจากหน้าเว็บ |
| `POST /favorites/add/<id>` · `/remove/<id>` | จัดการรายการโปรดจากหน้าเว็บ |
| `GET /watchlist` · `GET /favorites` | แสดงลิสต์ + ป้าย ★ + ดาวน์โหลด CSV + ลบรายรายการ |
| `GET /export/<kind>` | ดาวน์โหลดไฟล์ CSV (watchlist / favorites) |
| `GET /history` | ประวัติการค้นหาล่าสุด |
| เส้นทางอื่น / ข้อผิดพลาด | 404 · TMDB ล่ม 502 · ฐานข้อมูลเสีย → หน้าข้อผิดพลาดแบบสุภาพ |

### 2.4 กรณีขอบเขต (Edge Cases)

| กรณี | พฤติกรรมที่ต้องเกิด |
|---|---|
| ไม่มีคีย์ TMDB | ทุกหน้าเปิดได้ · หน้าค้นหาแจ้งวิธีตั้งค่าคีย์ · หน้าออฟไลน์ (ลิสต์/ประวัติ/CSV) ใช้ได้ปกติ |
| TMDB ล่ม / timeout | หน้าแจ้งแบบสุภาพ + ลองใหม่ได้ · ถ้าแคชยังสดแสดงผลจากแคชได้ |
| คีย์ผิด (401) · เรียกถี่เกิน (429) | ข้อความอธิบายชัดเจนตามแบบ Sprint 2 |
| คำค้นว่าง / ยาวเกิน / ไทย / emoji | ค้นได้หรือแจ้ง "ไม่พบ" — ไม่พัง |
| รหัสหนังไม่มีจริง (404) | หน้า "ไม่พบภาพยนตร์" แบบสุภาพ |
| ไฟล์ฐานข้อมูลเสีย | หน้าแจ้งปัญหา + วิธีแก้ (ย้าย/ลบไฟล์แล้วเริ่มใหม่) |
| เพิ่มซ้ำ · ลบของที่ไม่มี · URL ไม่มีอยู่ | ข้อความแจ้งผลชัดเจน · 404 แบบสุภาพ |

### 2.5 Definition of Done (สรุป — ผลการตรวจอยู่ในส่วนที่ 4)

- เปิดเว็บได้ครบทุกหน้า · ค้นหา/กรองเสมือน CLI · ลิสต์ + ★ + CSV ตรงกับข้อมูลจริง
- CLI เดิมยังทำงาน · ข้อมูลอยู่ข้ามการรีสตาร์ท
- flake8 + pytest ผ่านครบ · ไม่มีคีย์ในโค้ด/เทมเพลต/commit · CI เขียวต่อเนื่อง
"""

EXEC = """## ส่วนที่ 3: การพัฒนา (Execution)

ลำดับการพัฒนา: ① วางโครง `web/` และเพิ่ม dependency → ② สร้างหน้าจอและเส้นทางทั้งหมด →
③ Hardening ตามตารางกรณีขอบเขต → ④ เขียนชุดทดสอบเว็บใหม่ 40 เคส →
⑤ ตรวจรวม 133 เคส + flake8 ทั้งโปรเจกต์

โค้ดที่ส่งมอบทั้งชุดถูกฝังในเซลล์ด้านล่าง **ตามไฟล์จริงในโครงการทุกไบต์** —
โน้ตบุ๊กนี้สร้างด้วยสคริปต์ที่อ่านไฟล์จากโฟลเดอร์โค้ดโดยตรง รายงานกับโค้ดจึงไม่คลาดกัน
จากนั้นเซลล์สาธิตทั้งหมดจะรันจริงแบบ **ออฟไลน์ 100%** ด้วยตัวจำลอง TMDB ชุดเดียวกับชุดทดสอบ
(ไม่ต้องใช้คีย์หรืออินเทอร์เน็ต — รันซ้ำได้ทุกเครื่องและบน CI)

"""

DEMO_HEADER = """### 3.1 สาธิตการทำงานและกรณีขอบเขต (ผลลัพธ์จริงจากการรัน)

เซลล์ถัดไปรันเว็บแอปจริงผ่าน Flask test client และรัน CLI จริงโดยจำลองอินพุตผู้ใช้ (ไม่ใช่ภาพประกอบ) —
ทุกอย่างออฟไลน์ 100% และผลลัพธ์ที่เห็นคือผลจากการรันจริงในครั้งนี้
"""

RESULT = """## ส่วนที่ 4: ผลลัพธ์และการทดสอบ (Result)

### 4.1 สรุปความก้าวหน้าของงาน (Sprint Progress Summary)

- [x] เว็บแอปครบทุกหน้าจอตามข้อ 2.3 — ใช้บริการและฐานข้อมูลชุดเดียวกับ CLI (พิสูจน์ในเซลล์ "CLI + ฐานข้อมูลชุดเดียว")
- [x] ป้าย ★ ไขว้ลิสต์ · จำนวนรายการบนแถบนำทางอัปเดตทันที · ไฟล์ CSV ตรงกับลิสต์ปัจจุบันเสมอ
- [x] ชุดทดสอบ 133 เคส ผ่านครบทุกเคส — ชุดเดิม 93 เคสไม่ถูกแก้ไขแม้แต่ไฟล์เดียว + ใหม่ 40 เคสสำหรับเว็บ (ดูผลในเซลล์ pytest ด้านบน)
- [x] flake8 ผ่านทั้งโปรเจกต์ รวม `web/`
- [x] เอกสารประกอบรอบนี้: `sprint3/PLAN.md`
- [ ] ส่งมอบงานผ่าน Pull Request บน GitHub (จะเปิด PR เมื่อถึงขั้นส่งมอบตามข้อตกลงของทีม)

### 4.2 ผลการทดสอบกรณีขอบเขต (QA Report)

| รายการทดสอบ | อินพุต | ผลลัพธ์ที่คาดหวัง | ผลการทดสอบจริง | สถานะ |
|---|---|---|---|---|
| หน้าแรก + แถบนำทาง | `GET /` | เปิดได้ พร้อมจำนวนรายการจากฐานข้อมูล | HTTP 200 — แสดง "รายการรับชม (0)" | PASSED |
| ค้นหาบนเว็บ | `GET /search?q=alpha` | แสดงผลการค้นหา | HTTP 200 — พบ Alpha Signal | PASSED |
| รายละเอียด + หนังคล้าย | `GET /movie/101` | แสดงข้อมูลหนังและรายการคล้ายกัน | HTTP 200 — พบ Alpha Signal + Cobalt Night | PASSED |
| เพิ่มเข้า watchlist (เว็บ) | `POST /watchlist/add/101` | แจ้งผล + ยอดบนแถบนำทางอัปเดต | "เพิ่มเข้าสู่รายการรับชมแล้ว" · ยอด (1) | PASSED |
| เพิ่มซ้ำต้องไม่เพิ่ม | `POST` ซ้ำ | แจ้งว่ามีอยู่แล้ว | "เรื่องนี้อยู่ในรายการรับชมอยู่แล้ว" | PASSED |
| ป้าย ★ ไขว้ลิสต์ | หนังอยู่ทั้งสองลิสต์ | หน้า watchlist ขึ้น ★ | พบ ★ ข้างรายการ Cobalt Night | PASSED |
| ดาวน์โหลด CSV | `GET /export/watchlist` | ได้ไฟล์หัวตาราง + ข้อมูลตรงลิสต์ | HTTP 200 · attachment · หัวตาราง + 2 แถว (114 ไบต์) | PASSED |
| URL ไม่พบ | `/nope` | 404 แบบสุภาพ | HTTP 404 | PASSED |
| TMDB ล่ม | ค้นหาขณะ TMDB ผิดพลาด | หน้า 502 แบบสุภาพ | HTTP 502 — "เชื่อมต่อ TMDB ไม่สำเร็จ" | PASSED |
| ป้องกัน open redirect | `next` เป็น URL ภายนอก (แบบ backslash และ //) | ไม่พาออกจากแอป | Location ยังคงเป็นปลายทางภายใน (/movie/101?exists=watchlist) | PASSED |
| โหมดไม่มีคีย์ | เปิดทุกหน้าโดยไม่ตั้ง `TMDB_API_KEY` | เปิดได้ + แบนเนอร์วิธีตั้งค่า | แบนเนอร์แสดง · watchlist ใช้งานได้ (HTTP 200) | PASSED |
| CLI + เว็บ ฐานข้อมูลชุดเดียว | CLI เพิ่มรายการ → เปิดเว็บ | เห็นข้อมูลเดียวกัน | เว็บแสดง Alpha Signal · ยอด (1) | PASSED |

### 4.3 สรุปบทเรียน (Retrospective: Wow! & Whoops!)

**Wow! (ส่วนที่ทำได้ดี):**

- ไม่แตะโค้ดเดิม: `src/` ทั้ง 10 โมดูลเหมือนรอบก่อนทุกไบต์ — เว็บเชื่อมผ่านบริการเดิมล้วน ๆ
- ชุดทดสอบ 133 เคส ผ่านครบ + flake8 ทั้งโปรเจกต์ (รวม web/) — ชุดเดิม 93 เคสผ่านโดยไม่แก้ไฟล์
- ขอบเขตครบ: คีย์หาย · TMDB ล่ม · 404 · ฐานข้อมูลเสีย — ทุกกรณีมีหน้าและข้อความแบบสุภาพ

**Whoops! (ปัญหาและแนวทางแก้ไข):**

- SQLite ใช้ข้าม thread ไม่ได้ (เซิร์ฟเวอร์เว็บจัดการคำขอใน worker thread) — แก้โดยเปิด–ปิดการเชื่อมต่อใหม่ต่อหนึ่งคำขอ
- พบช่อง open redirect: ค่า next รูปแบบ backslash หลุดการตรวจ — แก้โดยปฏิเสธทั้ง backslash และ // พร้อมเทสต์ถาวรกันกลับมา (เซลล์ด้านบนแสดงให้เห็นว่าถูกบล็อกจริง)

### 4.4 ลิงก์และขั้นตอนถัดไป

- **Repository:** https://github.com/somjung/Movie-Discovery
- **เอกสารประกอบ:** `sprint3/PLAN.md` (แผนงาน + ตารางกรณีขอบเขต)
- **Sprint ถัดไป (Sprint สุดท้าย):** DevOps · CI/CD และการผสาน AI ตามคู่มือรายวิชา — ต่อยอดจากระบบที่สมบูรณ์รอบนี้
"""

FOOTER = """---

*หมายเหตุ: เซลล์สาธิตทั้งหมดในรายงานนี้รันแบบออฟไลน์ 100% — ใช้ตัวจำลอง TMDB ชุดเดียวกับชุดทดสอบ (`tests/fakes.py`) และฐานข้อมูลชั่วคราว จึงไม่ต้องใช้คีย์หรืออินเทอร์เน็ต และรันซ้ำได้ทุกเครื่อง · โน้ตบุ๊กนี้สร้างจากไฟล์โค้ดจริงในโปรเจกต์ด้วยสคริปต์ `build_notebook.py` · This product uses the TMDB API but is not endorsed or certified by TMDB.*
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
for folder in ("src", "tests", "data", "web", "web/templates", "web/static"):
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
%pip install -q pytest flake8 requests flask
import flask
import pytest
print("pytest", pytest.__version__, "| flask", flask.__version__)
'''

WEBWALK = '''# สาธิตเว็บแอปแบบออฟไลน์ผ่าน Flask test client (ตัวจำลอง TMDB + ฐานข้อมูลชั่วคราว)
import pathlib
import tempfile

from fakes import FakeTmdbClient
from src.movie_store import MovieStore
from web import create_app


def check(label, resp, needles):
    """แสดงสถานะ HTTP และรายการข้อความที่ต้องพบในหน้า"""
    html = resp.get_data(as_text=True)
    print(f"[{label}] HTTP {resp.status_code} | {len(html)} ตัวอักษร")
    for needle in needles:
        print("   -", ("พบ" if needle in html else "ไม่พบ"), "->", needle)


work = pathlib.Path(tempfile.mkdtemp(prefix="sprint3-web-"))
app = create_app(client=FakeTmdbClient(), store=MovieStore(":memory:"),
                 data_dir=str(work))
c = app.test_client()

check("หน้าแรก", c.get("/"), ["ระบบค้นพบภาพยนตร์", "รายการรับชม (0)"])
check("ค้นหา alpha", c.get("/search?q=alpha"), ["Alpha Signal"])
check("รายละเอียดหนัง 101", c.get("/movie/101"),
      ["Alpha Signal", "Cobalt Night"])

r = c.post("/watchlist/add/101", follow_redirects=True)
check("เพิ่ม 101 เข้า watchlist", r,
      ["เพิ่มเข้าสู่รายการรับชมแล้ว", "รายการรับชม (1)"])
r = c.post("/watchlist/add/101", follow_redirects=True)
check("เพิ่มซ้ำ (ต้องไม่เพิ่ม)", r, ["เรื่องนี้อยู่ในรายการรับชมอยู่แล้ว"])
r = c.post("/watchlist/add/103", follow_redirects=True)
check("เพิ่ม 103", r, ["รายการรับชม (2)"])
r = c.post("/favorites/add/103", follow_redirects=True)
check("เพิ่ม 103 เข้า favorites", r, ["เพิ่มเข้าสู่รายการโปรดแล้ว"])
check("หน้า watchlist (ป้าย ★ ไขว้ลิสต์)", c.get("/watchlist"),
      ["Cobalt Night", "★", "รายการรับชม (2)"])
check("หน้า favorites", c.get("/favorites"), ["Cobalt Night"])
check("ประวัติการค้นหา", c.get("/history"), ["alpha"])

r = c.get("/export/watchlist")
print(f"[ดาวน์โหลด watchlist.csv] HTTP {r.status_code} | {len(r.data)} ไบต์")
print("   ตัวอย่างเนื้อหา:", r.data.decode("utf-8").splitlines()[:2])
'''

EDGE = '''# กรณีขอบเขตและความปลอดภัยของเว็บ
from src.tmdb_client import TmdbError


class FlakyFake(FakeTmdbClient):
    """ตัวจำลองที่การค้นหาล้มเสมอ (จำลองสถานการณ์ TMDB ล่ม)"""

    def search_movies(self, query, page=1):
        raise TmdbError("HTTP 503 service unavailable")


check("URL ไม่มีอยู่", c.get("/nope"), ["ไม่พบหน้าที่ต้องการ"])

app2 = create_app(client=FlakyFake(), store=MovieStore(":memory:"),
                  data_dir=str(work))
check("TMDB ล่ม (502)", app2.test_client().get("/search?q=alpha"),
      ["เชื่อมต่อ TMDB ไม่สำเร็จ"])

bad = chr(92) * 2 + "evil.example"
r = c.post("/watchlist/add/101", data={"next": bad})
print("[open redirect: next แบบ backslash] HTTP", r.status_code,
      "| Location:", r.headers.get("Location"))
r = c.post("/watchlist/add/101", data={"next": "//evil.example"})
print("[open redirect: next แบบ //] HTTP", r.status_code,
      "| Location:", r.headers.get("Location"))

app3 = create_app(client=None, store=MovieStore(":memory:"),
                  data_dir=str(work))
c3 = app3.test_client()
check("โหมดไม่มีคีย์ — หน้าแรก", c3.get("/"), ["ยังไม่ได้ตั้งค่าคีย์"])
check("โหมดไม่มีคีย์ — ค้นหา", c3.get("/search?q=x"), ["TMDB_API_KEY"])
r = c3.get("/watchlist")
print(f"[โหมดไม่มีคีย์ — watchlist ยังใช้ได้] HTTP {r.status_code}")
'''

CLISHARED = '''# CLI เดิมยังทำงาน และใช้ฐานข้อมูลชุดเดียวกับเว็บ
from src.cli import CLI


def scripted(lines):
    """ฟังก์ชันอินพุตจำลอง: คืนค่าทีละบรรทัด แล้วส่ง EOF เมื่ออินพุตหมด"""
    queue = list(lines)

    def feed(prompt=""):
        if not queue:
            raise EOFError
        value = queue.pop(0)
        print(prompt + value)
        return value

    return feed


work5 = pathlib.Path(tempfile.mkdtemp(prefix="sprint3-shared-"))
db5 = str(work5 / "movies.db")
store5 = MovieStore(db5)
print("--- CLI เซสชัน: เพิ่มรายการลงฐานข้อมูลจริง ---")
CLI(input_func=scripted(["watchlist add 101", "quit"]), output_func=print,
    client=FakeTmdbClient(), store=store5, data_dir=str(work5)).run()
store5.close()

store6 = MovieStore(db5)
app5 = create_app(client=FakeTmdbClient(), store=store6, data_dir=str(work5))
check("เว็บอ่านฐานข้อมูลชุดเดียวกับ CLI", app5.test_client().get("/watchlist"),
      ["Alpha Signal", "รายการรับชม (1)"])
'''

PYTEST = '''# รันชุดทดสอบอัตโนมัติทั้ง 133 เคส (ออฟไลน์ 100% ไม่ต้องใช้คีย์จริง)
import sys
!{sys.executable} -m pytest -q
'''

FLAKE8 = '''# ตรวจสอบมาตรฐานโค้ด (PEP 8) ทั้งโปรเจกต์ รวมเว็บ
import sys
!{sys.executable} -m flake8 src tests web
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
    "web/__init__.py",
    "web/routes.py",
    "web/__main__.py",
    "web/templates/base.html",
    "web/templates/_card.html",
    "web/templates/home.html",
    "web/templates/search.html",
    "web/templates/movie.html",
    "web/templates/list.html",
    "web/templates/history.html",
    "web/templates/error.html",
    "web/static/style.css",
    "tests/conftest.py",
    "tests/fakes.py",
    "tests/test_tmdb_client.py",
    "tests/test_movie_store.py",
    "tests/test_discovery_flow.py",
    "tests/test_cli.py",
    "tests/test_web.py",
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
        code(WEBWALK),
        code(EDGE),
        code(CLISHARED),
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
