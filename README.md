# ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)

โครงงานปลายภาครายวิชา **CP352301 Script Programming (1/2569)** เป็นโปรแกรมภาษา Python แบบบรรทัดคำสั่ง (CLI) สำหรับค้นหาภาพยนตร์ที่คล้ายกับเรื่องที่ผู้ใช้ชื่นชอบ กรองและจัดอันดับผลลัพธ์ เก็บรายการรับชมส่วนตัว และส่งออกเป็นไฟล์ CSV

> This product uses the TMDB API but is not endorsed or certified by TMDB.

## สถานะของ Sprint

- **Sprint 1 (Front-End App Dev): เสร็จสมบูรณ์** โปรแกรม CLI แบบโต้ตอบมีข้อความต้อนรับ มีเมนูคำสั่ง รับและแปลงอินพุต (`.strip().lower()`) ตรวจสอบข้อมูลนำเข้าครบถ้วน และออกจากโปรแกรมอย่างสุภาพ ทั้งหมดสาธิตด้วยข้อมูลตัวอย่างที่ฝังอยู่ในโปรแกรม (ดูสเปกและ Definition of Done ใน `PLAN.md`)
- **Sprint 2 (Back-End): ขั้นถัดไป** เชื่อมต่อ TMDB API จริง เก็บข้อมูลลง SQLite และพัฒนาตรรกะการค้นหา/กรอง/จัดอันดับ โดยโมดูลพื้นฐานเตรียมไว้ใน `src/` พร้อมชุดทดสอบแล้ว (จะนำเสนอใน Sprint 2)
- **Sprint 3:** รวมระบบทั้งหมดเข้าด้วยกัน
- **Final:** DevOps/CI/CD และฟีเจอร์ AI

## ทีมและบทบาท

| บทบาท | สมาชิก |
|---|---|
| Planner / Team Leader | _(รอเพิ่มชื่อ)_ |
| Coder | นายอเสข ปัญญาวงค์ |
| Debugger / QA | _(รอเพิ่มชื่อ)_ |

## ฟีเจอร์ Sprint 1 (CLI)

- คำสั่งหลัก: `search <ชื่อเรื่อง>` `discover <รหัส>` `watchlist add|list|clear` `help` และ `quit` / `exit` / `q` / `ออก`
- รับคำสั่งได้ไม่ว่าพิมพ์ด้วยตัวพิมพ์เล็กหรือใหญ่ หรือมีช่องว่างหน้า-หลัง
- ตรวจสอบข้อมูลนำเข้าพร้อมข้อความแจ้งเตือนเป็นภาษาไทย โดยโปรแกรมไม่หยุดทำงานแม้ผู้ใช้จะป้อนข้อมูลผิด (`try / except ValueError` ครอบคลุมถึง EOF และ Ctrl+C)
- ครอบคลุมกรณีขอบเขตด้วยชุดทดสอบอัตโนมัติและการจำลองเซสชัน (ดู `PLAN.md`)

## เริ่มใช้งาน

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (บน Linux/macOS ใช้ source .venv/bin/activate)
pip install -r requirements.txt
python -m src.app               # เริ่มโปรแกรม CLI
```

## รายงาน Sprint 1 (เปิดใน Colab)

รายงานฉบับเต็มของ Sprint 1 (ข้อเสนอโครงการ แผนงาน การพัฒนา และผลลัพธ์) อยู่ในไฟล์ `notebooks/Sprint1_MovieDiscovery.ipynb` ถ้าต้องการรันซ้ำ ให้อัปโหลดไฟล์นี้ขึ้น Google Colab แล้วกด **Run all** ได้ทันที โดยใช้ข้อมูลตัวอย่างที่ฝังอยู่ในโปรแกรม (ไม่ต้องใช้คีย์ API)

## โครงสร้างโปรเจกต์

```
script-final-project/
├── PLAN.md              # สเปก Sprint 1 + Definition of Done (ผลงานของ Planner)
├── src/
│   ├── app.py           # จุดเริ่มโปรแกรม (python -m src.app)
│   ├── cli.py           # ส่วนติดต่อกับผู้ใช้ (Sprint 1)
│   ├── sample_data.py   # ข้อมูลตัวอย่างสำหรับสาธิต (ใช้จนกว่า API จริงจะเริ่มใน Sprint 2)
│   ├── tmdb_client.py   # [Sprint 2] ตัวเรียก TMDB API พร้อมจัดการข้อผิดพลาด
│   ├── movie_store.py   # [Sprint 2] ชั้นฐานข้อมูล SQLite
│   ├── discovery.py     # [Sprint 2] ตรรกะการตัดรายการซ้ำ กรอง และจัดอันดับ
│   ├── watchlist.py     # [Sprint 2] ตัวสร้างรายการ Top-N
│   ├── exporter.py      # [Sprint 2] ส่งออกไฟล์ CSV
│   └── config.py        # ค่าคงที่ + ที่ดึงคีย์ API
├── tests/               # ชุดทดสอบ pytest (CLI + โมดูลพื้นฐาน)
├── data/                # ไฟล์ฐานข้อมูล SQLite (สร้างใน Sprint ถัดไป)
├── notebooks/           # รายงาน Sprint 1 (pitch / แผนงาน / การพัฒนา / ผลลัพธ์)
├── tools/               # สคริปต์ช่วยสร้าง notebook (build_notebook.py)
└── .github/workflows/   # CI: flake8 + pytest ทุกครั้งที่ push
```

## ทดสอบและคุณภาพโค้ด

```bash
python -m pytest -q      # ชุดทดสอบ (ไม่ต้องใช้อินเทอร์เน็ต)
flake8 src tests         # ตรวจรูปแบบโค้ด (PEP 8)
```

CI: `.github/workflows/ci.yml` รัน flake8 และ pytest อัตโนมัติทุกครั้งที่ push (GitHub Actions)

## แผนงานถัดไป

- [x] Sprint 1: ส่วนติดต่อผู้ใช้ CLI (รอบนี้)
- [ ] Sprint 2: Back-End (TMDB จริง, SQLite, ค้นหา/กรอง/จัดอันดับ)
- [ ] Sprint 3: รวมระบบทั้งหมดและเก็บเคสขอบเขตให้แน่นขึ้น
- [ ] Final: DevOps, CI/CD, ฟีเจอร์ AI และเอกสาร/เดโมให้ครบชุด

## สัญญาอนุญาต (License)

MIT (ดูไฟล์ [LICENSE](LICENSE))
