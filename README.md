# ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)

โครงงานปลายภาครายวิชา **CP352301 Script Programming (1/2569)** พัฒนาด้วยภาษา Python — เริ่มจากโปรแกรมบรรทัดคำสั่ง (Sprint 1) ต่อด้วยระบบหลังบ้านจริง (Sprint 2) เว็บแอปที่ใช้ตรรกะชุดเดียวกัน (Sprint 3) และปิดท้ายด้วยฟีเจอร์ AI จริงบนเว็บ (Sprint 4) โดยแต่ละรอบพัฒนาต่อจากโค้ดของรอบก่อนหน้า


## สถานะของ Sprint

- **Sprint 1 (Front-End App Dev): เสร็จสมบูรณ์** โปรแกรม CLI แบบโต้ตอบ — ข้อความต้อนรับ · เมนูคำสั่ง · รับและแปลงอินพุต (`.strip().lower()`) · ตรวจสอบข้อมูลนำเข้า · ออกจากโปรแกรมอย่างสุภาพ (สาธิตด้วยข้อมูลตัวอย่างที่ฝังในโปรแกรม) → โค้ด: `sprint1/script-final-project/`
- **Sprint 2 (Back-End): เสร็จสมบูรณ์** เชื่อมต่อ TMDB จริง · เก็บข้อมูลลง SQLite · ค้นหา/กรอง/จัดอันดับ · รายการรับชม–รายการโปรด · ส่งออก CSV (เทสต์ 93 เคส) → โค้ด: `sprint2/script-final-project/`
- **Sprint 3 (รวมระบบเป็นเว็บแอป): เสร็จสมบูรณ์** เว็บแอป Flask ใช้บริการและฐานข้อมูลชุดเดียวกับ CLI (เทสต์รวม 133 เคส) → โค้ด: `sprint3/script-final-project/`
- **Sprint 4 (รอบสุดท้าย — DevOps, CI/CD & AI Integration): เสร็จสมบูรณ์** ฟีเจอร์ AI จริง 2 ตัว — ผู้ช่วยแนะนำ + สรุปภาษาไทยบนเว็บ (เทสต์รวม 199 เคส) · CI ตรวจโค้ดรอบล่าสุดอัตโนมัติ → โค้ด: `sprint4/script-final-project/` ← **เวอร์ชันล่าสุด**

## ทีมและบทบาท

บทบาทสลับกันในแต่ละรอบ Sprint:

| สมาชิก | Sprint 1 | Sprint 2–4 |
|---|---|---|
| อเสข ปัญญาวงค์ | Debugger | Coder |
| พลอยชมพู วงศ์กีรติกุล | Planner | Planner |
| นวมินทร์ คำจันทร์ | Coder | Debugger |

## ฟีเจอร์ (เวอร์ชันล่าสุด)

**CLI**

- ค้นหาภาพยนตร์ (TMDB จริง) · ดูรายละเอียด + หนังคล้ายกันพร้อมตัวกรอง (คะแนน · จำนวนโหวต · ปี · การเรียง · จำนวนผลลัพธ์)
- รายการรับชม / รายการโปรด · ประวัติการค้นหา · ส่งออกเป็นไฟล์ CSV
- ตรวจสอบข้อมูลนำเข้าพร้อมข้อความแจ้งเตือนภาษาไทย — โปรแกรมไม่หยุดทำงานแม้ผู้ใช้ป้อนข้อมูลผิด

**เว็บแอป (Sprint 3)**

- ฟีเจอร์ชุดเดียวกับ CLI ผ่านหน้าเว็บ (ฐานข้อมูล `data/movies.db` ชุดเดียวกัน)
- ตัวนับ "รายการรับชม (N) · รายการโปรด (M)" จากฐานข้อมูลจริงบนทุกหน้า · หน้าแจ้งข้อผิดพลาดอย่างสุภาพ

**AI (Sprint 4)**

- ผู้ช่วยแนะนำ (หน้า `/ai/recommend`) — เลือกหนังตั้งต้นจากลิสต์ของผู้ใช้ + พิมพ์โจทย์/อารมณ์ → AI คัด 3–5 เรื่องพร้อมเหตุผลภาษาไทย + ปุ่มเพิ่มเข้าลิสต์
- สรุปภาษาไทยในหน้ารายละเอียดหนัง — เนื้อเรื่อง 2–3 ประโยค + ทำไมควรดู 3 ข้อ (เก็บแคช · เปิดซ้ำไม่เรียก AI ซ้ำ)
- โหมดไม่มีคีย์ AI ยังใช้ระบบเดิมได้ครบ — หน้าแนะนำแสดงหนังคล้ายพื้นฐานแทน + แบนเนอร์วิธีตั้งค่า

## โครงสร้างโปรเจกต์

```
.
├── README.md
├── CHANGELOG.md                     # บันทึกการเปลี่ยนแปลงรายรอบ Sprint
├── .github/workflows/ci.yml         # CI: flake8 + pytest (ตรวจโค้ดเวอร์ชันล่าสุด)
├── sprint1/                         # งานส่งรอบที่ 1
│   ├── Sprint1_MovieDiscovery.ipynb # รายงาน Sprint 1 (ข้อเสนอ / แผนงาน / การพัฒนา / ผลลัพธ์)
│   └── script-final-project/        # โค้ดเวอร์ชัน Sprint 1 (เทสต์ 40 เคส)
├── sprint2/                         # งานส่งรอบที่ 2
│   ├── PLAN.md                      # แผนงาน Sprint 2
│   ├── Sprint2_MovieDiscovery.ipynb # รายงาน Sprint 2 (รันซ้ำได้แบบออฟไลน์)
│   └── script-final-project/        # โค้ดเวอร์ชัน Sprint 2 (TMDB จริง · SQLite — เทสต์ 93 เคส)
├── sprint3/                         # งานส่งรอบที่ 3
│   ├── PLAN.md                      # แผนงาน + สเปกเว็บ/Edge cases/DoD ของ Sprint 3
│   ├── Sprint3_MovieDiscovery.ipynb # รายงาน Sprint 3 (สาธิตเว็บแอป)
│   └── script-final-project/        # โค้ดเวอร์ชันปิดรอบ (เว็บแอป — เทสต์ 133 เคส)
└── sprint4/                         # งานส่งรอบที่ 4 (รอบสุดท้าย)
    ├── PLAN.md                      # แผนงาน + ขอบเขต/DoD ของ Sprint 4 (AI Integration)
    ├── Sprint4_MovieDiscovery.ipynb # รายงาน Sprint 4 (สาธิตฟีเจอร์ AI · ออฟไลน์ 100%)
    ├── build_notebook.py            # สคริปต์สร้างรายงานรอบ 4 จากไฟล์จริง
    ├── evidence/                    # หลักฐานการยิงจริง · การตรวจปิดรอบ · ทัวร์เบราว์เซอร์
    └── script-final-project/        # โค้ดเวอร์ชันล่าสุด (ฟีเจอร์ AI — เทสต์ 199 เคส)
```

> แต่ละรอบ Sprint พัฒนาต่อจากโค้ดของรอบก่อนหน้า และเก็บ **โค้ดเวอร์ชันปิดรอบ** ไว้ในโฟลเดอร์ของรอบนั้น — โค้ดเวอร์ชันล่าสุดที่ใช้พัฒนาต่อคือ `sprint4/script-final-project/`

## เริ่มใช้งาน

```bash
cd sprint4/script-final-project
python -m venv .venv
.venv\Scripts\activate          # Windows (บน Linux/macOS ใช้ source .venv/bin/activate)
pip install -r requirements.txt
python -m src.app               # เริ่มโปรแกรม CLI
python -m web                   # เริ่มเว็บแอป (ตั้งค่า TMDB_API_KEY สำหรับค้นหาจริง · DEEPSEEK_API_KEY สำหรับฟีเจอร์ AI — ไม่ตั้งคีย์ AI ก็ใช้ส่วนอื่นได้ครบ)
```

## รายงานและเอกสาร

- รายงาน Sprint 1 ฉบับเต็ม: `sprint1/Sprint1_MovieDiscovery.ipynb` — รันซ้ำได้บน Google Colab ด้วยข้อมูลตัวอย่างที่ฝังในโปรแกรม (ไม่ต้องใช้คีย์ API)
- รายงาน Sprint 2 ฉบับเต็ม: `sprint2/Sprint2_MovieDiscovery.ipynb` — รันซ้ำได้แบบออฟไลน์ 100% (ไม่ต้องใช้คีย์ API)
- รายงาน Sprint 3 ฉบับเต็ม: `sprint3/Sprint3_MovieDiscovery.ipynb` — สาธิตเว็บแอป · รันซ้ำได้แบบออฟไลน์ 100%
- รายงาน Sprint 4 ฉบับเต็ม: `sprint4/Sprint4_MovieDiscovery.ipynb` — สาธิตฟีเจอร์ AI (ผู้ช่วยแนะนำ + สรุปไทย) · รันซ้ำได้แบบออฟไลน์ 100%
- แผนงาน Sprint 2: `sprint2/PLAN.md`
- แผนงาน + สเปกละเอียดของ Sprint 3: `sprint3/PLAN.md`
- แผนงาน + สเปกของ Sprint 4 (รอบสุดท้าย): `sprint4/PLAN.md`
- บันทึกการเปลี่ยนแปลงรายรอบ Sprint: `CHANGELOG.md`

## ทดสอบและคุณภาพโค้ด

```bash
cd sprint4/script-final-project   # หรือโฟลเดอร์ Sprint ที่ต้องการตรวจ
python -m pytest -q               # รันออฟไลน์ ไม่ต้องใช้คีย์ API
flake8 src tests web              # ตรวจรูปแบบโค้ด PEP 8 (Sprint 1–2 ใช้ flake8 src tests)
```

จำนวนเทสต์รายรอบ: **Sprint 1 = 40** · **Sprint 2 = 93** · **Sprint 3 = 133** · **Sprint 4 (Final) = 199** (ผ่านทั้งหมด · flake8 สะอาดทุกรอบ)

CI: `.github/workflows/ci.yml` รัน flake8 และ pytest อัตโนมัติทุกครั้งที่ push (ตรวจโค้ดเวอร์ชันล่าสุดที่ `sprint4/script-final-project/`)

## แผนงานถัดไป

- [x] Sprint 1: ส่วนติดต่อผู้ใช้ CLI
- [x] Sprint 2: Back-End (TMDB จริง · SQLite · ค้นหา/กรอง/จัดอันดับ)
- [x] Sprint 3: รวมระบบเป็นเว็บแอป
- [x] Sprint 4 (Final): DevOps · CI/CD · ฟีเจอร์ AI จริง 2 ตัว · รายงาน/เด็ค/หลักฐานครบชุด — กำหนดส่งงาน 16/10/69
