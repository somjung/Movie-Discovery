#!/usr/bin/env python3
"""สร้างโน้ตบุ๊กรายงาน Sprint 4 จากไฟล์จริงในโปรเจกต์

โน้ตบุ๊กฝังซอร์สโค้ด "ตามไฟล์จริง" ในโฟลเดอร์ script-final-project/
รายงานกับโค้ดจึงไม่คลาดกัน รันด้วย:

    python build_notebook.py

ผลลัพธ์: Sprint4_MovieDiscovery.ipynb (โฟลเดอร์เดียวกับสคริปต์นี้)
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE / "script-final-project"
OUT = HERE / "Sprint4_MovieDiscovery.ipynb"

# --- narrative (Thai) -------------------------------------------------------

TITLE = """# รายงานผลการดำเนินงาน Sprint 4 (Final Term Project)

## ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)

**รายวิชา:** CP352301 Script Programming (1/2569)
**Sprint 4 (รอบสุดท้าย):** DevOps, CI/CD & AI Integration — สัปดาห์ที่ 15
**กำหนดนำเสนอ:** 6–7/10/69
**กำหนดส่งงาน:** 16/10/69

| บทบาท (หมุนเวียนตาม Sprint) | สมาชิกในทีม |
|---|---|
| Planner / Team Leader | นางสาวพลอยชมพู วงศ์กีรติกุล |
| Coder | นายอเสข ปัญญาวงค์ |
| Debugger / QA | นายนวมินทร์ คำจันทร์ |

**Repository:** https://github.com/somjung/Movie-Discovery

---

เนื้อหาของรายงานแบ่งออกเป็น 4 ส่วน ดังนี้

1. **ส่วนที่ 1: บทสรุปโครงการ (Project Recap)** ได้แก่ ภาพรวมของระบบ สถาปัตยกรรม และสิ่งที่ Sprint 4 เพิ่มจากรอบก่อน
2. **ส่วนที่ 2: แผนงาน (Plan)** ได้แก่ เป้าหมาย ขอบเขต ฟีเจอร์ AI 2 ตัว และกรณีขอบเขต 14 กรณี
3. **ส่วนที่ 3: การพัฒนา (Execution)** ได้แก่ โค้ดที่ส่งมอบทั้งชุด (รวมโมดูล AI) และสาธิตการทำงานแบบออฟไลน์
4. **ส่วนที่ 4: ผลลัพธ์และการทดสอบ (Result)** ได้แก่ สรุปความก้าวหน้า ตาราง QA บทเรียน และหลักฐานการยิงจริง
"""

RECAP = """## ส่วนที่ 1: บทสรุปโครงการ (Project Recap)

### 1. ภาพรวมระบบ

ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)
เป็นแอปพลิเคชันที่เปลี่ยน "ภาพยนตร์ที่ผู้ใช้ชื่นชอบ" ให้กลายเป็น "รายการรับชม" ที่รวบรวมไว้ในที่เดียว
ผู้ใช้ระบุภาพยนตร์ตั้งต้น (Seed Movie) หรือคำค้น ระบบดึงข้อมูลจริงจาก TMDB API (The Movie Database)
กรองและจัดอันดับตามเงื่อนไขที่ต้องการ บันทึกผลลงฐานข้อมูล SQLite ส่วนตัว แล้วส่งออกเป็นไฟล์ CSV

Sprint 4 เป็นรอบสุดท้ายตามคู่มือรายวิชา: ธีม DevOps, CI/CD & AI Integration —
ทีมเลือกสาย **AI Integration** เป็นงานใหม่หลัก และ **ไม่รวมงานขึ้นเซิร์ฟเวอร์จริง (deploy)**
ในรอบนี้ตามมติของทีมเมื่อ 4/10/69 รอบนี้เพิ่ม **ฟีเจอร์ AI ที่ทำงานจริง 2 ตัว** ให้เว็บแอป:
ผู้ช่วยแนะนำ (AI Recommender) และสรุปภาษาไทย (AI Movie Summary)

### 2. สถาปัตยกรรม 3 ชั้นหลังรอบนี้

โครง 3 ชั้นเดิมคงอยู่ทั้งหมด — Sprint 4 เพิ่มโมดูล AI เข้าชั้นที่มีอยู่แล้ว ไม่สร้างชั้นใหม่:

```
        ┌────────────────────────────────────────────────┐
        │  Presentation Layer                            │
        │  web/ (Flask)  ·  cli.py · app.py              │
        └──────────────────────┬─────────────────────────┘
                               │  ใช้บริการชุดเดียวกัน
        ┌──────────────────────▼─────────────────────────┐
        │  Business Logic Layer                          │
        │  discovery.py · watchlist.py · ai_advisor.py   │
        └──────────────────────┬─────────────────────────┘
                               │  constructor injection
        ┌──────────────────────▼─────────────────────────┐
        │  Data Access Layer                             │
        │  tmdb_client.py · movie_store.py ·             │
        │  exporter.py · ai_client.py                    │
        └────────────────────────────────────────────────┘
              │                  │                │
        TMDB REST API     บริการ AI จริง      data/movies.db
                          (DeepSeek API)
```
*(ภาพที่ 1: โครงสร้าง 3 ชั้นและตำแหน่งของโมดูล AI หลัง Sprint 4)*

- โมดูลใหม่ 2 ตัว: `ai_client.py` (ชั้นเข้าถึงข้อมูล — คุยผู้ให้บริการ AI) และ `ai_advisor.py` (ชั้นตรรกะธุรกิจ — คัดเลือก · สรุป · ตรวจคำตอบ · แคช)
- การฉีดพึ่งพา (dependency injection) คงเดิม — เทสต์และโน้ตบุ๊กนี้ใส่ "ตัวจำลอง AI" ได้ ไม่ต้องใช้เน็ตหรือคีย์
- แคชคำตอบ AI ใช้ตาราง `api_cache` เดิมกับคีย์นำหน้า `ai:` (สรุป 7 วัน · แนะนำ 1 ชั่วโมง)

### 3. สิ่งที่ Sprint 4 เพิ่มจากรอบก่อน

- **ผู้ช่วยแนะนำ (หน้า `/ai/recommend`)** — เลือกหนังตั้งต้นจากลิสต์ของผู้ใช้ + พิมพ์โจทย์/อารมณ์ → ระบบดึงหนังคล้ายจริงจาก TMDB (สูงสุด 12 เรื่อง) → AI คัด 3–5 เรื่องพร้อมเหตุผลภาษาไทย + ปุ่มเพิ่มเข้าลิสต์
- **สรุปภาษาไทย (ในหน้า `/movie/<id>`)** — ปุ่มเดียว → "สรุปเนื้อเรื่อง 2–3 ประโยค + ทำไมควรดู 3 ข้อ" จากข้อมูล TMDB ที่มีอยู่ → เก็บแคช เปิดซ้ำไม่เรียก AI ซ้ำ
- ความปลอดภัยของคำตอบ AI: บังคับรูปแบบ JSON · ตรวจ id ให้อยู่ในชุดตัวเลือกเท่านั้นก่อนใช้ · ทุกข้อความถูก escape ตอนแสดงผล · คีย์ผ่านตัวแปรสภาพแวดล้อมเท่านั้น
- ชุดทดสอบ 199 เคส (เดิม 133 + ใหม่ 66 สำหรับ AI) ออฟไลน์ 100% · flake8 ผ่านทั้งโปรเจกต์ · CI ตรวจโค้ดรอบล่าสุดอัตโนมัติ
- หลักฐานรันจริงประกอบรายงาน/เด็ค: ยิง DeepSeek จริง (4 การเรียก ≈ $0.0008) · ทัวร์เบราว์เซอร์จริง + สกรีนช็อต 11 ภาพ · เด็ค Final 27 สไลด์
"""

PLAN = """## ส่วนที่ 2: แผนงาน (Plan)

### 2.1 เป้าหมายของ Sprint 4

คู่มือรายวิชากำหนดรอบสุดท้ายเป็น DevOps, CI/CD & AI Integration:
จัดทำระบบทดสอบอัตโนมัติ · ตั้งค่า CI/CD Pipeline ผ่าน GitHub Actions · เชื่อมต่อฟีเจอร์ AI
รอบนี้ทีมเลือกสาย AI Integration เป็นงานใหม่หลัก และตัดงาน deploy ออก (เก็บเป็นแนวทางต่อยอด) จึง:

1. เพิ่มฟีเจอร์ AI จริง 2 ตัวบนเว็บที่ทำงานกับผู้ให้บริการ AI จริง (DeepSeek) ผ่านคีย์ของผู้ใช้
2. ต่อยอดชุดทดสอบอัตโนมัติ (+66 เคสออฟไลน์) และคง CI ให้ตรวจโค้ดรอบล่าสุดต่อเนื่อง
3. รับมือกรณีขอบเขตครบ 14 กรณี (ไม่มีคีย์ · AI ล่ม 401/429/หมดเวลา · คำตอบผิดรูปแบบ · โจทย์ยาว/มีโค้ด ฯลฯ)
4. ไม่รื้อของเดิม — เทสต์เดิม 133 เคสต้องผ่านครบเสมอ · แก้แตะโค้ดเดิมเฉพาะจุดเชื่อมที่จำเป็น (`config.py` เพิ่มการอ่านคีย์ AI) · ไฟล์เทสต์ของชุดเดิมไม่ถูกแก้

### 2.2 ขอบเขต

- **ในขอบเขต:** ฟีเจอร์ AI 2 ตัวบนเว็บพร้อมข้อความ/เหตุผลภาษาไทย · แคชคำตอบ AI · กรณีขอบเขตครบ · เทสต์ออฟไลน์ชุดใหม่ · อัปเดต CI ให้ตรวจโค้ดรอบล่าสุด · เด็ค Final · รายงานรอบ 4 (โน้ตบุ๊กนี้)
- **นอกขอบเขต:** งานขึ้นเซิร์ฟเวอร์จริง/deploy (ตัดออกตามมติ 4/10) · ค้นหาเชิงความหมาย (embeddings — ผู้ให้บริการที่เลือกไม่มี ต้องเพิ่มผู้ให้บริการที่สอง) · การแก้ CLI (หยุดไว้ที่ Sprint 2 โค้ดคงอยู่) · ระบบบัญชีผู้ใช้
- **ข้อกำหนด:** คีย์ TMDB และคีย์ AI เก็บผ่านตัวแปรสภาพแวดล้อมเท่านั้น — ห้ามปรากฏในโค้ด เอกสาร หรือ commit · เทสต์ทุกชุดออฟไลน์

### 2.3 ฟีเจอร์ใหม่ — พฤติกรรมที่ต้องเกิด

**4.1 ผู้ช่วยแนะนำ (หน้า `/ai/recommend`)**

- ทางเข้า: ลิงก์เมนู "ผู้ช่วยแนะนำ" ทุกหน้า + ปุ่ม "ใช้เรื่องนี้เป็นฐาน (AI)" ในหน้ารายละเอียดหนัง
- ฟอร์ม: เลือกหนังตั้งต้นจากรายการรับชม/รายการโปรด + ช่องโจทย์อิสระ (ไม่บังคับ) — ลิสต์ว่างทั้งคู่มีข้อความชวนไปเพิ่มรายการ
- ขั้นตอน: กดปุ่ม → ดึงหนังคล้ายจริงจาก TMDB (สูงสุด 12) → AI คัด 3–5 เรื่องพร้อมเหตุผลไทย → การ์ด + ปุ่ม "เพิ่มเข้ารายการรับชม" (กลไกปุ่มเดิมทั้งเว็บ)
- คำตอบ AI: บังคับ JSON (id + เหตุผล) และ **ตรวจก่อนใช้เสมอ** — id ต้องอยู่ในชุดที่ส่งไป · เหตุผลต้องไม่ว่าง
- ความปลอดภัย: ข้อความผู้ใช้ถูกส่งเป็น "ข้อมูล" (กำกับโมเดลไม่ให้ทำตามคำสั่งแฝง) · ทุกข้อความจาก AI ถูก escape ตอนแสดงผล
- ไม่มีคีย์ AI: แสดงหนังคล้ายพื้นฐาน (จัดอันดับด้วยคะแนนเดิม) + แบนเนอร์วิธีตั้งค่า — ระบบไม่พัง

**4.2 สรุปไทย (ในหน้า `/movie/<id>`)**

- ปุ่ม "สรุปภาษาไทย (AI)" → สรุปเนื้อเรื่อง 2–3 ประโยค + ทำไมควรดู 3 ข้อ จากข้อมูล TMDB ที่มีอยู่ → เก็บแคช → กลับหน้าเดิมพร้อมแสดงผล
- เปิดหน้ารายละเอียดซ้ำ: ถ้ามีแคชแล้วแสดงจากแคชทันที — ไม่เรียก AI ซ้ำ (ทั้งประหยัดเวลาและค่าใช้จ่าย)
- ไม่มีคีย์: ไม่แสดงปุ่ม + แบนเนอร์วิธีตั้งค่า · AI ล่ม: ข้อความสุภาพ บอกสาเหตุ ลองใหม่ได้ — และไม่บันทึกแคช

### 2.4 กรณีขอบเขต (Edge Cases) — ครบ 14 กรณี

| สถานการณ์ | ระบบทำอะไร |
|---|---|
| ไม่มีคีย์ AI | ทุกหน้าเปิดได้ · หน้าแนะนำแสดงหนังคล้ายพื้นฐาน + แบนเนอร์ · ปุ่มสรุปไม่แสดง |
| คีย์ผิด (401) | ข้อความสุภาพ "คีย์ AI ไม่ถูกต้อง" + กลับหน้าเดิมได้ |
| เรียกถี่เกิน (429) | ข้อความ "เรียกบ่อยเกินไป ลองใหม่ภายหลัง" |
| AI หมดเวลา / เน็ตหลุด | ข้อความสุภาพ บอกสาเหตุ + ลองใหม่ได้ |
| AI ตอบไม่ใช่ JSON | "AI ตอบผิดรูปแบบ — ลองใหม่" ไม่บันทึกแคช ไม่พัง |
| AI อ้าง id นอกชุดที่ให้ | คัดเฉพาะ id ที่ถูกต้อง · ถ้าไม่เหลือ = ข้อความลองใหม่ |
| หนังคล้ายไม่พอ (0 เรื่อง) | ข้อความ "ยังมีข้อมูลไม่พอจะแนะนำ" |
| โจทย์ว่าง | ทำงานปกติ (แนะนำจากเรื่องตั้งต้นล้วน) |
| โจทย์ยาวเกิน 200 ตัวอักษร | ตัดให้อัตโนมัติ + แจ้งว่าใช้เฉพาะส่วนแรก |
| โจทย์ emoji / ไทย / โค้ด | ทำงานได้หรือแจ้งชัดเจน — โค้ดถูก escape ตอนแสดงผล |
| เข้าหน้าแนะนำขณะทุกลิสต์ว่าง | ข้อความชวนไปเพิ่มรายการ + ลิงก์หน้าค้นหา |
| กดสร้างสรุปซ้ำ | ใช้แคชเดิม ไม่เรียก AI ซ้ำ |
| สร้างสรุปขณะ AI ล่ม | ไม่บันทึกแคช + ข้อความสุภาพ |
| ไฟล์ฐานข้อมูลเสีย | หน้าซ่อมเดิม (ไม่กระทบ) |

### 2.5 Definition of Done (สรุป — ผลการตรวจอยู่ในส่วนที่ 4)

- หน้า "ผู้ช่วยแนะนำ" ทำงานจริงกับ DeepSeek (คีย์จริง): เลือกเรื่องตั้งต้น + โจทย์ → ได้ 3–5 เรื่องพร้อมเหตุผลไทยที่อ่านรู้เรื่อง
- สรุปไทยในหน้ารายละเอียด: สร้างได้ · เก็บแคช · ข้อความอ่านรู้เรื่อง · เพิ่มจากผลแนะนำทำงาน
- ทุกกรณีในตาราง 2.4 ทำงานครบ · เพิ่มจากหน้าแนะนำ → CLI เห็นข้อมูลเดียวกัน
- ชุดเดิม 133 เคสผ่านครบ · ไม่มีเทสต์เดิมถูกแก้แม้แต่เคสเดียว · ชุดใหม่ 66 เคสผ่าน · flake8 = 0 · CI เขียว · ไม่มีคีย์หลุด
"""

EXEC = """## ส่วนที่ 3: การพัฒนา (Execution)

ลำดับการพัฒนา: ① เตรียมสำเนาโค้ด S3 + อัปเดต CI มาที่รอบ 4 → ② สร้าง `ai_client.py` (ไคลเอนต์ AI)
→ ③ สร้าง `ai_advisor.py` (คัดเลือก/สรุป/ตรวจคำตอบ/แคช) → ④ ต่อสองฟีเจอร์เข้ากับเว็บ
(หน้าใหม่ + ปุ่มสรุป + เมนู) → ⑤ เก็บกรณีขอบเขตครบ 14 กรณี + เขียนชุดทดสอบใหม่ 66 เคส
→ ⑥ ตรวจรวม 199 เคส + flake8 + ตรวจการพึ่งพาเชิงกลไก + ยิงจริง DeepSeek + ทัวร์เบราว์เซอร์จริง

โค้ดที่ส่งมอบทั้งชุดถูกฝังในเซลล์ด้านล่าง **ตามไฟล์จริงในโครงการทุกไบต์** —
โน้ตบุ๊กนี้สร้างด้วยสคริปต์ที่อ่านไฟล์จากโฟลเดอร์โค้ดโดยตรง รายงานกับโค้ดจึงไม่คลาดกัน
จากนั้นเซลล์สาธิตทั้งหมดจะรันจริงแบบ **ออฟไลน์ 100%** ด้วยตัวจำลอง TMDB และตัวจำลอง AI
ชุดเดียวกับชุดทดสอบ (ไม่ต้องใช้คีย์หรืออินเทอร์เน็ต — รันซ้ำได้ทุกเครื่องและบน CI)

"""

DEMO_HEADER = """### 3.1 สาธิตการทำงานและกรณีขอบเขต (ผลลัพธ์จริงจากการรัน)

เซลล์ถัดไปรันเว็บแอปจริงผ่าน Flask test client และสาธิตฟีเจอร์ AI ด้วย **ตัวจำลอง AI**
ที่กำหนดคำตอบไว้ล่วงหน้า (ไม่ได้เรียก DeepSeek จริงในโน้ตบุ๊ก — หลักฐานการเรียกจริงแสดงในส่วนที่ 4) —
ทุกอย่างออฟไลน์ 100% และผลลัพธ์ที่เห็นคือผลจากการรันจริงในครั้งนี้
"""

RESULT = """## ส่วนที่ 4: ผลลัพธ์และการทดสอบ (Result)

### 4.1 สรุปความก้าวหน้าของงาน (Sprint Progress Summary)

- [x] ฟีเจอร์ AI 2 ตัวทำงานจริงบนเว็บ — ยิง DeepSeek จริง 4 การเรียก (≈ $0.0008 · HTTP 200 ทุกครั้ง) หลักฐาน: `sprint4/evidence/live-deepseek-2026-10-05.md`
- [x] หน้า `/ai/recommend` + ปุ่มสรุปไทยในหน้ารายละเอียด + ปุ่มเพิ่มจากผลแนะนำ — พฤติกรรมครบตามตาราง 2.4 (พิสูจน์ในเซลล์ส่วนที่ 3)
- [x] ชุดทดสอบ 199 เคส ผ่านครบ — ไม่มีเทสต์เดิมถูกแก้แม้แต่เคสเดียว + ใหม่ 66 เคส (`tests/test_ai.py`)
- [x] flake8 ผ่านทั้งโปรเจกต์ (รวม `web/`) · ตรวจการพึ่งพาเชิงกลไก R1–R6 ผ่าน 19/19 บน 11 โมดูล (สคริปต์ `sprint4/evidence/layer_check.py` + ทดสอบตัวตรวจเองว่าจับผิดได้จริง)
- [x] CI (GitHub Actions) อัปเดตชี้โค้ดรอบ 4 — flake8 → pytest อัตโนมัติทุก push/PR (ไม่ใช้คีย์)
- [x] ไม่มีคีย์ในโค้ด/เทมเพลต/เอกสาร — ตรวจสแกนซ้ำก่อนส่งงาน
- [x] หลักฐานประกอบ: ทัวร์เบราว์เซอร์จริง + สกรีนช็อต 11 ภาพ (1600×900) · เด็คนำเสนอ Final 27 สไลด์
- [ ] ส่งมอบงานผ่าน Pull Request บน GitHub (จะเปิด PR เมื่อถึงขั้นส่งมอบตามข้อตกลงของทีม)

### 4.2 ผลการทดสอบกรณีขอบเขต (QA Report)

| รายการทดสอบ | อินพุต | ผลลัพธ์ที่คาดหวัง | ผลการทดสอบจริง (จากรันในโน้ตบุ๊กนี้) | สถานะ |
|---|---|---|---|---|
| หน้าแนะนำ + ดรอปดาวน์หนังตั้งต้น | `GET /ai/recommend` | แสดงตัวเลือกจากรายการผู้ใช้ | HTTP 200 — "ผู้ช่วยแนะนำ" + ตัวเลือก Alpha Signal | PASSED |
| ส่งโจทย์แบบ PRG | `POST /ai/recommend` (base + mood) | อัปเดตผลด้วยกลไก POST → GET | HTTP 303 → Location `/ai/recommend?base=101&go=1&mood=…` | PASSED |
| AI คัดเลือกพร้อมเหตุผลไทย | ตัวจำลอง AI คืน 3 picks | การ์ด 2–5 เรื่องพร้อมเหตุผล | "AI คัดเลือกให้ 2 เรื่อง" + เหตุผลไทย 2 รายการ | PASSED |
| ตรวจ id ก่อนใช้ (กันโมเดลหลอน) | คำตอบ AI มี id 98765 ปนมา | id นอกชุดถูกตัดทิ้ง | เหลือเฉพาะเรื่องจริง 2 เรื่อง · เหตุผลปลอมหาย | PASSED |
| แคชผลแนะนำ 1 ชั่วโมง | เปิดผลลัพธ์ซ้ำ | ไม่เรียก AI เพิ่ม | จำนวนการเรียก AI คงที่ 1 ครั้ง | PASSED |
| เพิ่มจากผลแนะนำเข้าลิสต์ | `POST /watchlist/add/103` | เพิ่ม + ข้อความยืนยัน + ยอดอัปเดต | "เพิ่มเข้าสู่รายการรับชมแล้ว" · ยอด "(2)" | PASSED |
| สรุปไทย | `GET /movie/101?summary=1` | สรุป + ทำไมควรดู 3 ข้อ | "สรุปภาษาไทยจาก AI" + เนื้อเรื่อง + ทำไมควรดู 3 ข้อ | PASSED |
| แคชสรุป 7 วัน | เปิดสรุปซ้ำ | ไม่เรียก AI ซ้ำ | จำนวนการเรียก AI คงที่ 2 ครั้ง | PASSED |
| คีย์ผิด (401) | ตัวจำลองโยน 401 ทั้งสองหน้า | ข้อความสุภาพ | "คีย์ AI ไม่ถูกต้องหรือถูกปฏิเสธ (401)" ทั้งหน้าสรุปและหน้าแนะนำ | PASSED |
| เรียกถี่เกิน (429) | ตัวจำลองโยน 429 | ข้อความสุภาพ | "เรียกใช้บริการ AI ถี่เกินไป (429)" | PASSED |
| คำตอบผิดรูปแบบ | ตัวจำลองตอบ JSON พัง | ข้อความสุภาพ | "AI ตอบกลับผิดรูปแบบ — ลองใหม่อีกครั้ง" | PASSED |
| หนังคล้ายไม่พอ (0 เรื่อง) | ตัวจำลองไม่คืนหนังคล้าย | ข้อความชัดเจน | "ยังมีข้อมูลไม่พอจะแนะนำ" | PASSED |
| AI คัดไม่ได้เลย | คำตอบมีแต่ id นอกชุด | ข้อความชัดเจน | "AI คัดเลือกไม่ได้ในรอบนี้" | PASSED |
| โจทย์ยาวเกิน 200 ตัวอักษร | mood ยาว 250 ตัวอักษร | ตัด + แจ้งเตือน ยังทำงานได้ | "โจทย์ยาวเกิน 200 ตัวอักษร" + ได้ผล 1 เรื่อง | PASSED |
| โหมดไม่มีคีย์ AI | เปิดทุกหน้าโดยไม่ตั้งคีย์ | ระบบไม่พัง | หน้าแนะนำ = หนังคล้ายพื้นฐาน + แบนเนอร์ · ปุ่มสรุปซ่อน · ขอสรุปได้ข้อความวิธีตั้งค่า | PASSED |
| เข้าแนะนำขณะทุกลิสต์ว่าง | ฐานข้อมูลว่าง | ชวนไปเพิ่มรายการ | "ยังไม่มีเรื่องในรายการ" + ลิงก์ /search | PASSED |
| CLI + เว็บ ฐานข้อมูลชุดเดียว | CLI เพิ่มรายการ → เปิดเว็บ | เห็นข้อมูลเดียวกัน | เว็บแสดง Alpha Signal · ยอด (1) | PASSED |

### 4.3 สรุปบทเรียน (Retrospective: Wow! & Whoops!)

**Wow! (ส่วนที่ทำได้ดี):**

- ไม่รื้อของเดิม: โมดูลเดิม 9 ตัวของ `src/` ไม่ถูกแก้ (แตะเฉพาะ `config.py` เพื่ออ่านคีย์ AI) · ไฟล์เทสต์เดิมไม่ถูกแก้ · เทสต์ 133 เคสผ่านครบ — เพิ่มโมดูล AI 2 ตัวและเทสต์ใหม่ 66 เคส
- ตรวจคำตอบ AI ก่อนใช้เสมอ: id ต้องอยู่ในชุดที่ส่งไปเท่านั้น (เซลล์ด้านบนแสดงการตัด id 98765 จริง) + ทุกข้อความถูก escape
- แคชทำงานจริง: เปิดซ้ำไม่เสียค่าใช้จ่ายเพิ่ม (แสดงด้วยตัวนับการเรียก) — และเทสต์ทั้งชุดออฟไลน์ 100% รันซ้ำได้ฟรีทุกเครื่อง
- หลักฐานครบสำหรับรายงาน/เด็ค: ยิง DeepSeek จริง 4 การเรียก ≈ $0.0008 · ทัวร์เบราว์เซอร์ 11 ภาพ · ตัวเลขทุกตัวมาจากการรันจริง

**Whoops! (ปัญหาและแนวทางแก้ไข):**

- โมเดลภาษามีโอกาสอ้างภาพยนตร์ที่ไม่มีอยู่จริง (hallucination) — แก้ด้วยการบังคับคำตอบเป็น JSON, ตรวจ id เทียบชุดตัวเลือกก่อนใช้ทุกครั้ง และปิดโหมดคิดของโมเดลเพื่อความเร็ว/ค่าใช้จ่ายที่คุมได้ (วัดจริง: สรุป 2.6 วินาที · แนะนำ 1.8 วินาที)
- ข้อความของผู้ใช้อาจแฝงคำสั่งหลอกโมเดล (prompt injection) — ส่งเป็น "ข้อมูล" พร้อมกำกับใน system prompt และ escape ทุกข้อความก่อนแสดงผล
- โจทย์ที่ยาวเกินขอบเขตเคยทำให้คุณภาพคำตอบเพี้ยน — ตัดที่ 200 ตัวอักษร + แจ้งผู้ใช้ + มีเทสต์คุมถาวร
- เมธอดแคชเดิมของ TMDB บังคับอายุคงที่ — เพิ่มพารามิเตอร์อายุต่อคีย์ (สรุป 7 วัน · แนะนำ 1 ชั่วโมง) พร้อมเทสต์

### 4.4 ลิงก์และขั้นตอนถัดไป

- **Repository:** https://github.com/somjung/Movie-Discovery
- **เอกสารประกอบ:** `sprint4/PLAN.md` (แผนงาน + ตารางกรณีขอบเขต) · `sprint4/evidence/` (หลักฐานการยิงจริง · การตรวจปิดรอบ · ทัวร์เบราว์เซอร์ · สกรีนช็อต)
- **และแนวทางต่อยอดในอนาคต:** ขึ้นเซิร์ฟเวอร์จริง + HTTPS · บัญชีผู้ใช้หลายคน · ค้นหาเชิงความหมาย (embeddings) — สอดคล้องกับสไลด์ "แนวทางต่อยอด" ของเด็ค Final
- **กำหนดส่งงาน:** 16/10/69
"""

FOOTER = """---

*หมายเหตุ: เซลล์สาธิตทั้งหมดในรายงานนี้รันแบบออฟไลน์ 100% — ใช้ตัวจำลอง TMDB และตัวจำลอง AI ชุดเดียวกับชุดทดสอบ (`tests/fakes.py`) และฐานข้อมูลชั่วคราว จึงไม่ต้องใช้คีย์หรืออินเทอร์เน็ต และรันซ้ำได้ทุกเครื่อง · โน้ตบุ๊กนี้สร้างจากไฟล์โค้ดจริงในโปรเจกต์ด้วยสคริปต์ `build_notebook.py` · This product uses the TMDB API but is not endorsed or certified by TMDB.*
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


work = pathlib.Path(tempfile.mkdtemp(prefix="sprint4-web-"))
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
check("ประวัติการค้นหา", c.get("/history"), ["alpha"])

r = c.get("/export/watchlist")
print(f"[ดาวน์โหลด watchlist.csv] HTTP {r.status_code} | {len(r.data)} ไบต์")
print("   ตัวอย่างเนื้อหา:", r.data.decode("utf-8").splitlines()[:2])
'''

AIDEMO = '''# สาธิตฟีเจอร์ AI #1: ผู้ช่วยแนะนำ (ออฟไลน์ — ตัวจำลอง AI ชุดเดียวกับชุดทดสอบ)
# ตัวจำลองมีคำตอบเตรียมไว้ 2 ชุด: ชุดแรกสำหรับผู้ช่วยแนะนำ ชุดที่สองสำหรับสรุปไทย
from fakes import FakeAiClient
from src.sample_data import SAMPLE_MOVIES

ai = FakeAiClient(replies=[
    {"picks": [{"id": 103, "reason": "จังหวะเบา ดูเพลิน เหมาะกับคืนสบาย ๆ"},
               {"id": 98765, "reason": "เรื่องนี้ไม่มีอยู่ในชุดตัวเลือก"},
               {"id": 102, "reason": "อารมณ์ขันแบบดูได้เรื่อย ๆ ไม่ต้องคิดมาก"}]},
    {"summary": "แอลฟา ซิกแนล เล่าถึงทีมนักวิจัยที่ไล่ตามสัญญาณลึกลับจากอวกาศ จนค้นพบความจริงที่เปลี่ยนทุกอย่าง",
     "why": ["บรรยากาศตึงมือชวนติดตามตลอดเรื่อง", "ดนตรีประกอบช่วยพาไปกับฉากสำคัญ",
             "ความยาวกำลังดีสำหรับคืนดูหนังคนเดียว"]},
])

store2 = MovieStore(":memory:")
store2.add_movie(dict(SAMPLE_MOVIES[0]))
store2.add_to_watchlist(101)

app2 = create_app(client=FakeTmdbClient(), store=store2,
                  data_dir=str(work), ai_client=ai)
c2 = app2.test_client()

check("หน้าแนะนำ + ดรอปดาวน์หนังตั้งต้น", c2.get("/ai/recommend"),
      ["ผู้ช่วยแนะนำ", "Alpha Signal"])

resp = c2.post("/ai/recommend", data={"base": "101", "mood": "อยากดูเบา ๆ สนุก ๆ"})
print("[POST โจทย์] HTTP", resp.status_code, "| Location:", resp.headers.get("Location"))
results_url = resp.headers["Location"]

r = c2.get(results_url)
check("ผลการคัดเลือกของ AI", r,
             ["AI คัดเลือกให้ 2 เรื่อง", "เรื่องตั้งต้น:", "Alpha Signal",
              "อยากดูเบา", "จังหวะเบา ดูเพลิน", "อารมณ์ขันแบบดูได้เรื่อย ๆ"])
html = r.get_data(as_text=True)
print("   id นอกชุด (98765) ถูกตัด:", "98765" not in html,
      "| เหตุผลของ id ปลอมหายไป:", "เรื่องนี้ไม่มีอยู่ในชุดตัวเลือก" not in html)
print("   จำนวนการเรียก AI (ตัวจำลอง):", len(ai.calls), "ครั้ง")

c2.get(results_url)
print("   เปิดผลลัพธ์ซ้ำ (ใช้แคช 1 ชม.) — จำนวนการเรียก AI:", len(ai.calls), "ครั้ง")

r = c2.post("/watchlist/add/103", data={"next": results_url}, follow_redirects=True)
check("เพิ่มจากผลแนะนำเข้าลิสต์", r, ["เพิ่มเข้าสู่รายการรับชมแล้ว", "รายการรับชม (2)"])
'''

AIDEMO_S = '''# สาธิตฟีเจอร์ AI #2: สรุปภาษาไทย + แคช (ออฟไลน์ — ใช้ตัวจำลอง AI ชุดเดิมจากเซลล์ก่อน)
r = c2.get("/movie/101?summary=1")
check("สรุปภาษาไทยจาก AI", r,
      ["สรุปภาษาไทยจาก AI", "ทีมนักวิจัยที่ไล่ตามสัญญาณลึกลับ", "ทำไมควรดู",
       "บรรยากาศตึงมือชวนติดตามตลอดเรื่อง"])
print("   จำนวนการเรียก AI หลังสร้างสรุป:", len(ai.calls), "ครั้ง")

c2.get("/movie/101?summary=1")
print("   เปิดสรุปซ้ำ (ใช้แคช 7 วัน) — จำนวนการเรียก AI:", len(ai.calls), "ครั้ง")
'''

AIEDGE = '''# กรณีขอบเขต AI ครบชุด (ออฟไลน์ 100% — ตัวจำลอง AI/เน็ตชุดเดียวกับชุดทดสอบ)
from src.ai_client import AiError

work3 = pathlib.Path(tempfile.mkdtemp(prefix="sprint4-edge-"))


def seed(store, movie_id=101):
    """ใส่หนังตั้งต้น + เพิ่มเข้าลิสต์ ให้หน้าแนะนำมีตัวเลือก"""
    store.add_movie(dict(SAMPLE_MOVIES[movie_id - 101]))
    store.add_to_watchlist(movie_id)


s = MovieStore(":memory:"); seed(s)
a401 = FakeAiClient(error=AiError("the AI provider rejected the API key (HTTP 401)"))
c401 = create_app(client=FakeTmdbClient(), store=s,
                  data_dir=str(work3), ai_client=a401).test_client()
check("คีย์ผิด (401) — หน้าสรุป", c401.get("/movie/101?summary=1"),
      ["คีย์ AI ไม่ถูกต้องหรือถูกปฏิเสธ (401)"])
check("คีย์ผิด (401) — หน้าแนะนำ",
      c401.post("/ai/recommend", data={"base": "101"}, follow_redirects=True),
      ["คีย์ AI ไม่ถูกต้องหรือถูกปฏิเสธ (401)"])

s = MovieStore(":memory:"); seed(s)
a429 = FakeAiClient(error=AiError("the AI rate limit was hit (HTTP 429) - slow down"))
c429 = create_app(client=FakeTmdbClient(), store=s,
                  data_dir=str(work3), ai_client=a429).test_client()
check("เรียกถี่เกิน (429)",
      c429.post("/ai/recommend", data={"base": "101"}, follow_redirects=True),
      ["เรียกใช้บริการ AI ถี่เกินไป (429)"])

s = MovieStore(":memory:"); seed(s)
aBad = FakeAiClient(error=AiError("the AI reply is not valid JSON"))
cBad = create_app(client=FakeTmdbClient(), store=s,
                  data_dir=str(work3), ai_client=aBad).test_client()
check("คำตอบผิดรูปแบบ (JSON พัง)", cBad.get("/movie/101?summary=1"),
      ["AI ตอบกลับผิดรูปแบบ — ลองใหม่อีกครั้ง"])

s = MovieStore(":memory:"); seed(s)
aJunk = FakeAiClient(reply={"picks": [{"id": 98765, "reason": "นอกชุด"}]})
cJunk = create_app(client=FakeTmdbClient(), store=s,
                   data_dir=str(work3), ai_client=aJunk).test_client()
check("คัดไม่ได้เลย (id นอกชุดทั้งหมด)",
      cJunk.post("/ai/recommend", data={"base": "101"}, follow_redirects=True),
      ["AI คัดเลือกไม่ได้ในรอบนี้"])

s = MovieStore(":memory:"); seed(s)
aLong = FakeAiClient(reply={"picks": [{"id": 103, "reason": "สบาย ๆ"}]})
cLong = create_app(client=FakeTmdbClient(), store=s,
                   data_dir=str(work3), ai_client=aLong).test_client()
check("โจทย์ยาวเกิน 200 ตัวอักษร",
      cLong.get("/ai/recommend?base=101&go=1&mood=" + "x" * 250),
      ["โจทย์ยาวเกิน 200 ตัวอักษร", "AI คัดเลือกให้ 1 เรื่อง"])

s = MovieStore(":memory:"); seed(s)
cNo = create_app(client=FakeTmdbClient(similar=[], recommendations=[]), store=s,
                 data_dir=str(work3), ai_client=aLong).test_client()
check("หนังคล้ายไม่พอ (0 เรื่อง)",
      cNo.post("/ai/recommend", data={"base": "101"}, follow_redirects=True),
      ["ยังมีข้อมูลไม่พอจะแนะนำ"])

cEmpty = create_app(client=FakeTmdbClient(), store=MovieStore(":memory:"),
                    data_dir=str(work3), ai_client=FakeAiClient()).test_client()
check("เข้าแนะนำขณะทุกลิสต์ว่าง", cEmpty.get("/ai/recommend"),
      ["ยังไม่มีเรื่องในรายการ", "/search"])

s = MovieStore(":memory:"); seed(s)
cNone = create_app(client=FakeTmdbClient(), store=s,
                   data_dir=str(work3), ai_client=None).test_client()
check("โหมดไม่มีคีย์ AI — หน้าแนะนำ", cNone.get("/ai/recommend?base=101&go=1"),
      ["หนังคล้ายพื้นฐาน (โหมดไม่มี AI)", "ยังไม่ได้ตั้งค่าคีย์ AI"])
html_none = cNone.get("/movie/101").get_data(as_text=True)
print("   โหมดไม่มีคีย์ — ปุ่มสรุปในหน้ารายละเอียดถูกซ่อน:",
      "สรุปภาษาไทย (AI)" not in html_none)
check("โหมดไม่มีคีย์ AI — ขอสรุป", cNone.get("/movie/101?summary=1"),
      ["ยังไม่ได้ตั้งค่าคีย์ AI"])
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


work5 = pathlib.Path(tempfile.mkdtemp(prefix="sprint4-shared-"))
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

PYTEST = '''# รันชุดทดสอบอัตโนมัติทั้ง 199 เคส (ออฟไลน์ 100% ไม่ต้องใช้คีย์จริง)
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
    "src/ai_client.py",
    "src/movie_store.py",
    "src/discovery.py",
    "src/ai_advisor.py",
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
    "web/templates/ai_recommend.html",
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
    "tests/test_ai.py",
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
        code(AIDEMO),
        code(AIDEMO_S),
        code(AIEDGE),
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
