# ตรวจปิดรอบ — ขั้น 10 (Sprint 4)

**วันที่:** 2026-10-14 (รันจริงบนเครื่องผู้พัฒนา) · **Python:** venv ของโปรเจกต์ 3.11.15 · **เอกสารนี้บันทึกผลจริง ไม่ใช่การประมาณ**

สคริปต์ตรวจ import อยู่ในโฟลเดอร์นี้: `layer_check.py` (รันซ้ำได้ทุกรอบ — วิธีใช้ท้ายไฟล์)

---

## 1. pytest ทุกรอบ — ผ่านครบ (ออฟไลน์ 100% ไม่ใช้เน็ต/ไม่ใช้คีย์)

```
sprint1/script-final-project   →  40 passed in 0.54s
sprint2/script-final-project   →  93 passed in 1.12s
sprint3/script-final-project   → 133 passed in 1.88s
sprint4/script-final-project   → 199 passed in 2.44s   ← รอบล่าสุด
```

รายไฟล์ของรอบล่าสุด (sprint4):

```
tests/test_ai.py              66 เคส  (ไคลเอนต์ AI · ตรรกะแนะนำ/สรุป · หน้าจอ AI)
tests/test_cli.py             42 เคส
tests/test_discovery_flow.py  24 เคส
tests/test_movie_store.py     13 เคส
tests/test_tmdb_client.py     14 เคส
tests/test_web.py             40 เคส
รวม                          199 เคส
```

## 2. flake8 — 0 ทุกชุด

```
sprint1: flake8 src tests      → exit 0
sprint2: flake8 src tests      → exit 0
sprint3: flake8 src tests web  → exit 0
sprint4: flake8 src tests web  → exit 0
```

## 3. ตรวจ import เชิงกลไก (R1–R6) — 11 โมดูล · ผ่าน 19/19

วิธี: สแกน AST ของทุกไฟล์ใน `src/` (11 โมดูล) สร้างกราฟการ import แล้วตรวจ 6 กฎ — กฎ R4/R5 ปรับตามแผน Sprint 4 ข้อ 3 (เพิ่มโมดูล AI)

```
R1/R3 ทิศทาง — ห้ามโมดูล import ชั้นที่สูงกว่าตัวเอง          PASS (11 โมดูล)
R2    ชั้นธุรกิจพึ่งชั้นข้อมูล "ผ่านพารามิเตอร์" เท่านั้น       PASS
      (อนุโลมเฉพาะคลาสข้อผิดพลาด — ใช้จริง 1 จุด ดูด้านล่าง)
R4    requests — เฉพาะ tmdb_client · ai_client (ปรับจากเดิม)  PASS
R5    sqlite3 → movie_store · csv → exporter ·               PASS
      json → tmdb_client · ai_client · ai_advisor (เพิ่ม S4)
R6    ไม่มี import วัฏจักร                                   PASS
รวมทุกจุดตรวจ: 19/19
```

จุดที่ต้องรู้จากกราฟ (แสดงครบ ไม่ตัด):

- `ai_advisor → ai_client` — จุดเดียวที่ชั้นธุรกิจอ้างถึงโมดูลชั้นข้อมูล: อ้างเฉพาะ "คลาสข้อผิดพลาด" (AiError) เพื่อส่งสัญญาณข้อความสุภาพให้ชั้นเว็บ — ทิศทางลงล่าง ไม่เกิดวัฏจักร และตัวตรวจยืนยันด้วย AST ว่า AiError สืบทอด Exception จริง (เทียบรอบ Sprint 2: ชั้นธุรกิจไม่ import ข้ามชั้นเลย)
- เส้นเชื่อมภายใน 11 เส้น: app→cli · cli→config,discovery,exporter,movie_store,tmdb_client,watchlist · tmdb_client→config,movie_store · ai_client→config · ai_advisor→ai_client
- ไลบรารีภายนอก 13 จุดใน 7 โมดูล: requests ×2 · sqlite3 ×1 · csv ×1 · json ×3 · os ×4 · urllib.parse ×1 · hashlib ×1

## 4. ทดสอบตัวตรวจเอง (negative test — "ตัวตรวจต้องจับผิดได้จริง")

คัดลอก `src/` ไปโฟลเดอร์ชั่วคราว แล้วเติม import ผิดกฎ 3 จุด:

```
watchlist.py  +=  import requests                     → ต้องจับที่ R4
discovery.py  +=  from .cli import CLI                → ต้องจับที่ทิศทาง (R1)
watchlist.py  +=  from .movie_store import MovieStore → ต้องจับที่ R2
```

ผล: จับได้ครบทั้ง 3 จุด + พบวัฏจักร cli↔discovery ที่โค้ดที่เติมสร้างขึ้น == **15/19 (exit 1)**

จากนั้นรันซ้ำบนโค้ดจริง → **19/19 (exit 0)** — ยืนยันว่าผล "ผ่าน" มาจากโค้ดที่สะอาดจริง ไม่ใช่ตัวตรวจที่ไม่จับอะไรเลย

## 5. ขอบเขตและหมายเหตุ

- ตรวจเฉพาะ `src/` (11 โมดูล) — สโคปเดียวกับรอบ Sprint 2 (9 โมดูล ตอนนั้นผ่าน 51/51 ตามบันทึก) · `web/` (ชั้นนำเสนอ) ไม่อยู่ในข้อบังคับของชุดนี้ — ข้อมูลประกอบ: flask อยู่เฉพาะ `web/` · `web/__init__.py` จับ `sqlite3.Error` สำหรับหน้าซ่อมฐานข้อมูล (ฟีเจอร์เดิมตั้งแต่ Sprint 3)
- คีย์ทั้งสองยังตั้งเป็นตัวแปรระดับผู้ใช้ (DEEPSEEK 35 ตัวอักษร · TMDB 32 ตัวอักษร) — ไม่มีค่าใดปรากฏในไฟล์หรือเอาต์พุตของรอบนี้
- ชุดเทสต์ทุกตัวออฟไลน์ (ตัวจำลอง) — รันซ้ำได้ฟรี

## 6. ตัวเลขพร้อมใช้สำหรับเด็ค/รายงาน (จากผลรันจริง)

```
เทสต์รวมทุกยุค     40 → 93 → 133 → 199   (Sprint 1 → 4)
เทสต์ใหม่รอบ S4   66 เคส (เพิ่มจาก 133 เป็น 199)
flake8             0 ทุกชุด (ทั้ง 4 รอบ)
ตรวจ import        R1–R6 ผ่าน 19/19 บน 11 โมดูล
ยิงจริง DeepSeek   4 การเรียก · HTTP 200 ทุกตัว · ~$0.0008
                   (5/10 — ดู live-deepseek-2026-10-05.md)
```

## วิธีรันซ้ำ

```
cd sprint4/evidence
python layer_check.py             # ตรวจ src ของ sprint4 (exit 0 = ผ่าน)
python layer_check.py <path/src>  # ตรวจชุดอื่น เช่นโฟลเดอร์สำเนา
```
