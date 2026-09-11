#!/usr/bin/env python3
"""Rebuild notebooks/Sprint1_MovieDiscovery.ipynb from the repository files.

The Sprint 1 submission notebook embeds the delivered source exactly as it
exists in this repository, so the notebook and the code can never drift
apart. Run from anywhere with:

    python tools/build_notebook.py

Output: sprint1/Sprint1_MovieDiscovery.ipynb
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "Sprint1_MovieDiscovery.ipynb"

# --- narrative (Thai) -----------------------------------------------------

TITLE = """# รายงานผลการดำเนินงาน Sprint 1 (Final Term Project)

## ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)

**รายวิชา:** CP352301 Script Programming (1/2569)
**Sprint 1:** Front-End App Dev (สัปดาห์ที่ 12)
**กำหนดนำเสนอ:** 15–16/9/69
**กำหนดส่งงาน:** 18/9/69

| บทบาท (หมุนเวียนตาม Sprint) | สมาชิกในทีม |
|---|---|
| Planner / Team Leader | [ชื่อนักศึกษา] |
| Coder | นายอเสข ปัญญาวงค์ |
| Debugger / QA | [ชื่อนักศึกษา] |

**Repository:** https://github.com/somjung/Movie-Discovery

---

เนื้อหาของรายงานแบ่งออกเป็น 4 ส่วน ดังนี้

1. **ส่วนที่ 1: ข้อเสนอโครงการ (Project Pitch)** ได้แก่ ภาพรวมของโครงงาน ปัญหา แนวทางแก้ไข ขอบเขต และคุณสมบัติหลัก
2. **ส่วนที่ 2: แผนงาน (Plan)** ได้แก่ ขอบเขตงานและ Definition of Done ของ Sprint 1
3. **ส่วนที่ 3: การพัฒนา (Execution)** ได้แก่ โค้ดที่ส่งมอบและตัวอย่างการทำงานจริงของโปรแกรม
4. **ส่วนที่ 4: ผลลัพธ์และการทดสอบ (Result)** ได้แก่ ผลการทดสอบกรณีขอบเขต บทเรียนที่ได้ และลิงก์ของโปรเจกต์
"""

PITCH = """## ส่วนที่ 1: ข้อเสนอโครงการ (Project Pitch)

### 1. ชื่อโครงงาน (Project Title)

**ระบบค้นพบภาพยนตร์และสร้างรายการรับชม (Movie Discovery & Watchlist Builder)**

### 2. ปัญหาที่โครงงานต้องการแก้ (Problem Statement)

ปัจจุบันแพลตฟอร์มสตรีมมิง (Streaming Platform) นำเสนอภาพยนตร์ชุดเดียวกันให้ผู้ชมทุกคน ทำให้การค้นพบภาพยนตร์ที่ตรงกับรสนิยมของแต่ละบุคคลเป็นเรื่องยาก และต้องใช้เวลาค้นหาหรือทดลองรับชมหลายรอบ นอกจากนี้ ผู้ชมจำนวนมากยังจดรายชื่อภาพยนตร์ที่ต้องการรับชมไว้กระจัดกระจายหลายแห่ง เช่น บันทึกในโทรศัพท์ แชทส่วนตัว หรือรายการโปรดของแต่ละแพลตฟอร์ม ส่งผลให้รายการเหล่านั้นสูญหาย ถูกหลงลืม หรือไม่ถูกนำมาใช้จริง โครงงานนี้จึงมีเป้าหมายเพื่อเปลี่ยน "ภาพยนตร์ที่ผู้ใช้ชื่นชอบ" ให้กลายเป็น "รายการรับชม" ที่รวบรวมไว้ในที่เดียวอย่างเป็นระบบ

### 3. แนวทางแก้ปัญหา (Proposed Solution)

โครงงานนี้พัฒนาระบบในรูปแบบแอปพลิเคชันบรรทัดคำสั่ง (Command-Line Application) ที่ทำงานบนเครื่องของผู้ใช้โดยไม่ต้องใช้เซิร์ฟเวอร์ ผู้ใช้ระบุภาพยนตร์ตั้งต้น (Seed Movie) หรือเงื่อนไขที่ต้องการ เช่น ประเภทภาพยนตร์ (Genre) นักแสดง หรือผู้กำกับ ระบบจะเรียกข้อมูลจาก TMDB API (The Movie Database) เพื่อดึงรายชื่อภาพยนตร์ที่คล้ายกัน (Similar) และรายการที่ระบบแนะนำ (Recommendations) จากนั้นจึงกรองและจัดอันดับตามเงื่อนไขของผู้ใช้ เช่น ช่วงปี คะแนนขั้นต่ำ และความยาวของเรื่อง บันทึกผลลงคลังภาพยนตร์ส่วนตัวในฐานข้อมูล SQLite สร้างเป็นรายการ Top-10 (10 เรื่องน่าชม) และส่งออกเป็นไฟล์ CSV (Comma-Separated Values)

จุดเด่นของโครงงาน กล่าวคือ ข้อมูลภาพยนตร์ที่คล้ายกันได้มาจาก API โดยตรง ขณะที่ตรรกะการคัดเลือก การจัดอันดับ การจัดการคลังข้อมูล และการส่งออก เป็นส่วนที่ทีมพัฒนาขึ้นเองทั้งหมด

ขอบเขต: โครงงานไม่รวมการเล่นวิดีโอ (Playback) หรือการดาวน์โหลดเนื้อหาภาพยนตร์ มุ่งเน้นเฉพาะการค้นพบ การจัดเก็บ และการส่งออกรายการเท่านั้น

```
  seed: movie / genre / actor / director
        │
        ▼
  TMDB fetch (search · discover · similar · recommendations)
        │
        ▼
  filter + rank (year · rating · runtime · dedupe)
        │
        ▼
  SQLite library ──▶ Top-10 watchlist ──▶ CSV export
```
*(ภาพที่ 1: ลำดับขั้นตอนการทำงานหลักของระบบ)*

### 4. หมวดหมู่โครงงาน (Domain)

การวิเคราะห์และจัดการข้อมูล (Data Analysis & Management)
### 5. API ที่ใช้งาน (APIs to Use)

**API หลัก**
- ชื่อ API: TMDB (The Movie Database) API
- ลิงก์เอกสาร: https://developer.themoviedb.org/
- ประเภทข้อมูล: ข้อมูลภาพยนตร์ (ชื่อเรื่อง ปี ประเภท นักแสดง ผู้กำกับ โปสเตอร์) รายการภาพยนตร์ที่คล้ายกัน (Similar) และรายการที่ระบบแนะนำ (Recommendations)

**API เสริม**
- ชื่อ API: OMDb API
- ลิงก์เอกสาร: https://www.omdbapi.com/
- ประเภทข้อมูล: คะแนนจาก IMDb, Rotten Tomatoes และ Metacritic

รูปแบบการรับส่งข้อมูล: JSON ผ่าน HTTP GET ทั้งสองบริการมีคีย์สำหรับการใช้งานฟรี โดย TMDB อนุญาตการใช้งานที่ไม่ใช่เชิงพาณิชย์และกำหนดให้แสดงข้อความให้เครดิตว่า "This product uses the TMDB API but is not endorsed or certified by TMDB." ส่วน OMDb รุ่นฟรีจำกัด 1,000 คำขอต่อวัน

### 6. แผนการจัดเก็บข้อมูล (Data Persistence Plan)

- ฐานข้อมูลขนาดเล็ก (Mini Database): SQLite จัดเก็บข้อมูลหลัก 6 ส่วน ได้แก่ ภาพยนตร์ (movies), ความเชื่อมโยงภาพยนตร์คล้ายกัน (similar_links), รายการรับชม (watchlist), รายการโปรด (favorites), ประวัติการค้นหา (searches) และแคชผลลัพธ์จาก API (api_cache)
- ไฟล์ข้อมูล (File-based): CSV ส่งออกรายการรับชมเพื่อนำไปใช้ต่อ
- ข้อมูลทั้งหมดจัดเก็บอยู่บนเครื่องของผู้ใช้ ไม่มีส่วนเซิร์ฟเวอร์

### 7. รูปแบบการเขียนโปรแกรม (Framework Style)

การเขียนโปรแกรมเชิงวัตถุ (Object-Oriented Programming: OOP)

โครงสร้างคลาสหลัก ได้แก่ TmdbClient (เชื่อมต่อและเรียก API), MovieStore (จัดการฐานข้อมูล), DiscoveryService (ตรรกะการค้นพบและคัดกรอง), WatchlistBuilder (สร้างรายการ Top-10), Exporter (ส่งออก CSV) และ CLI (ส่วนติดต่อผู้ใช้)

### 8. บทบาทและความรับผิดชอบ (Roles & Responsibilities)

- Project Manager / CI-CD Integrator: [ชื่อเพื่อนร่วมทีมคนที่ 1]
- Automated Tester & QA: [ชื่อเพื่อนร่วมทีมคนที่ 2]
- Core Developer(s): นายอเสข ปัญญาวงค์

### 9. คุณสมบัติหลัก (MVP Features)

1. **ค้นหาและสำรวจภาพยนตร์**: ค้นหาด้วยชื่อเรื่อง และสำรวจตามประเภท นักแสดง หรือผู้กำกับ ผ่าน TMDB
2. **ค้นพบภาพยนตร์ที่คล้ายกัน**: แสดงรายชื่อภาพยนตร์คล้ายกันและรายการแนะนำจากภาพยนตร์ตั้งต้นที่ผู้ใช้เลือก
3. **สร้างรายการ Top-10**: กรองตามช่วงปี คะแนนขั้นต่ำ และความยาว ตัดรายการซ้ำ และตัดภาพยนตร์ที่บันทึกไว้แล้วออก
4. **คลังภาพยนตร์ส่วนตัว**: บันทึกข้อมูลลง SQLite พร้อมรายการโปรดและประวัติการค้นหา
5. **ส่งออกและนำไปใช้ต่อ**: ส่งออกรายการรับชมเป็นไฟล์ CSV

### 10. คุณสมบัติเสริม (Stretch Features — Optional)

- แสดงช่องทางรับชม (Watch Providers) ตามภูมิภาคของแต่ละเรื่อง (ข้อมูลจาก TMDB)
- สุ่มเลือกภาพยนตร์สำหรับการรับชมประจำคืน (Movie Night Picker)
- แผนภูมิสรุปสถิติ เช่น คะแนนและแนวโน้ม ด้วย matplotlib
- โหมดออฟไลน์สำหรับการนำเสนอ โดยใช้แคชที่บันทึกไว้

### 11. รายการตรวจสอบการประเมิน (Evaluation Checklist)

- [ ] API ทำงานได้ (เรียกข้อมูลแบบ GET จัดการข้อผิดพลาด และแปลงข้อมูล JSON)
- [ ] ข้อมูลถูกจัดเก็บอย่างถูกต้อง (SQLite และการส่งออก CSV)
- [ ] โค้ดเป็นไปตามมาตรฐาน PEP 8 (ตรวจด้วย flake8 หรือ black)
- [ ] ทดสอบอัตโนมัติด้วย pytest (จำลองการเรียก API ด้วย Mock)
- [ ] กระบวนการ CI/CD ทำงาน (GitHub Actions)
- [ ] เอกสาร README ครอบคลุมการติดตั้งและการใช้งาน
- [ ] ระบุบทบาทของสมาชิกในทีมอย่างชัดเจน"""


PLAN = """## ส่วนที่ 2: แผนงาน (Plan)

### 2.1 เป้าหมายและขอบเขตของ Sprint 1

**เป้าหมาย:** พัฒนาส่วนติดต่อกับผู้ใช้ (Presentation Layer) ของโปรแกรม ให้ผู้ใช้สั่งงานผ่านเมนูคำสั่งได้สะดวก
โดยมีข้อความต้อนรับ มีเมนูที่อ่านง่าย รับคำสั่ง แปลงอินพุต
และตรวจสอบความถูกต้องของข้อมูลที่ป้อนเข้ามาทุกครั้ง ที่สำคัญคือโปรแกรมต้องไม่หยุดทำงานแม้ผู้ใช้จะป้อนข้อมูลผิดพลาด

**ขอบเขตของ Sprint 1:** พัฒนาโปรแกรมแบบ CLI ที่รับคำสั่งจากผู้ใช้ มีเมนูและระบบตรวจสอบข้อมูลนำเข้า
จัดการข้อผิดพลาดได้ครบถ้วน และมีชุดทดสอบอัตโนมัติประกอบ

**สิ่งที่ยังไม่รวมใน Sprint นี้ (จะพัฒนาใน Sprint 2 เป็นต้นไป):** การเชื่อมต่อ TMDB API จริง ฐานข้อมูล SQLite
อัลกอริทึมค้นหา/กรอง/เรียงลำดับ และการส่งออก CSV
สำหรับใน Sprint นี้ คำสั่ง `search` และ `discover` จะสาธิตด้วยข้อมูลตัวอย่างที่ฝังไว้ในโปรแกรมไปก่อน

### 2.2 คำสั่งของระบบ

| คำสั่ง | อินพุต | พฤติกรรมที่คาดหวัง |
|---|---|---|
| `search <ชื่อเรื่อง>` | ข้อความ | ค้นหาภาพยนตร์จากชื่อเรื่องด้วยข้อมูลตัวอย่าง ถ้าไม่พบจะแจ้งให้ทราบ |
| `discover <รหัส>` | จำนวนเต็มมากกว่า 0 | แสดงรายชื่อภาพยนตร์ที่คล้ายกัน เรียงตามคะแนนจากมากไปน้อย |
| `watchlist add <รหัส>` | จำนวนเต็มมากกว่า 0 | เพิ่มภาพยนตร์เข้ารายการรับชม ไม่เพิ่มซ้ำ |
| `watchlist list` / `clear` | — | แสดงหรือล้างรายการรับชม |
| `help` | — | แสดงคำสั่งทั้งหมด |
| `quit` / `exit` / `q` / `ออก` | — | ออกจากโปรแกรมทันที ไม่ว่าพิมพ์แบบใด |

### 2.3 Definition of Done (ผลการตรวจสอบอยู่ในส่วนที่ 4)

- [ ] พิมพ์ `quit` แบบตัวพิมพ์เล็ก ตัวพิมพ์ใหญ่ หรือมีช่องว่างหน้า-หลัง โปรแกรมต้องออกทันทีพร้อมข้อความอำลา
- [ ] พิมพ์คำสั่งที่ไม่รู้จัก โปรแกรมต้องแจ้งเตือนและกลับสู่เมนู ไม่หยุดทำงาน
- [ ] กด Enter โดยไม่พิมพ์อะไร โปรแกรมต้องแจ้งเตือน "กรุณาพิมพ์คำสั่ง"
- [ ] ป้อนรหัสภาพยนตร์ที่ไม่ใช่ตัวเลข (เช่น `abc`) โปรแกรมต้องแจ้งเตือนโดยไม่หยุดทำงาน
- [ ] ป้อนรหัสภาพยนตร์ติดลบหรือศูนย์ โปรแกรมต้องปฏิเสธพร้อมข้อความแจ้ง
- [ ] อินพุตสิ้นสุด (EOF) หรือผู้ใช้กด Ctrl+C โปรแกรมต้องออกอย่างสุภาพ
- [ ] โค้ดต้องผ่านการตรวจด้วย flake8 และทุกเมธอดต้องมี docstring
"""

EXEC = """## ส่วนที่ 3: การพัฒนา (Execution)

ขั้นตอนถัดไปจะเริ่มจากการสร้างโครงสร้างโปรเจกต์ตามที่กำหนดไว้ใน `PLAN.md` จากนั้นจึงเขียนโค้ดทั้งหมด
ที่ส่งมอบใน Sprint นี้ และปิดท้ายด้วยการสาธิตการทำงานของโปรแกรมโดยจำลองอินพุตเหมือนมีผู้ใช้งานพิมพ์คำสั่งจริง
"""

RESULT = """## ส่วนที่ 4: ผลลัพธ์และการทดสอบ (Result)

### 4.1 สรุปความก้าวหน้าของงาน (Sprint Progress Summary)

- [x] ออกแบบโครงสร้างระบบและกำหนด Definition of Done ไว้ใน `PLAN.md`
- [x] พัฒนาฟังก์ชันหลักครบตามแผน ได้แก่ `display_welcome_message`, `get_command_input`, ส่วนเมนูและตัวจัดการคำสั่ง และลูปหลัก `run`
- [x] ดักจับข้อผิดพลาดด้วย `try / except` ครอบคลุมทั้งอินพุตผิดรูปแบบ อินพุตสิ้นสุด (EOF) และการกด Ctrl+C
- [x] ทดสอบอัตโนมัติของ CLI จำนวน 20 เคส ผ่านครบทุกเคส (ดูผลได้จากเซลล์ pytest ด้านบน) และทดสอบซ้ำด้วยการจำลองเซสชันการใช้งานจริง
- [ ] ส่งมอบงานผ่าน Pull Request บน GitHub (repo: https://github.com/somjung/Movie-Discovery)

### 4.2 ผลการทดสอบกรณีขอบเขต (QA Report)

| รายการทดสอบ | อินพุต | ผลลัพธ์ที่คาดหวัง | ผลการทดสอบจริง | สถานะ |
|---|---|---|---|---|
| ออกจากโปรแกรมด้วยตัวพิมพ์ใหญ่ | `QUIT` | แสดงข้อความอำลาและออกจากโปรแกรม | แสดงข้อความอำลาและหลุดจากลูปทำงาน | PASSED |
| ออกจากโปรแกรมโดยมีช่องว่างหน้า-หลัง | `   Quit   ` | แสดงข้อความอำลาและออกจากโปรแกรม | ตัดช่องว่างก่อนประมวลผล แล้วออกจากโปรแกรมได้ตามปกติ | PASSED |
| พิมพ์คำสั่งที่ไม่รู้จัก | `asdf` | แจ้งเตือนและกลับสู่เมนู | แจ้งเตือนว่าไม่รู้จักคำสั่ง และกลับสู่เมนู | PASSED |
| กด Enter โดยไม่พิมพ์อะไร | (บรรทัดว่าง) | แจ้งเตือนโดยไม่หยุดทำงาน | แจ้งเตือนให้พิมพ์คำสั่งก่อน | PASSED |
| ป้อนรหัสภาพยนตร์ที่ไม่ใช่ตัวเลข | `discover abc` | แจ้งเตือนโดยไม่หยุดทำงาน | แจ้งว่า "รหัสภาพยนตร์ต้องเป็นตัวเลข" | PASSED |
| ป้อนรหัสภาพยนตร์ติดลบหรือศูนย์ | `discover -3`, `0` | ปฏิเสธพร้อมข้อความแจ้ง | แจ้งว่า "รหัสภาพยนตร์ต้องมากกว่า 0" | PASSED |
| ค้นหาภาพยนตร์ตามปกติ | `search alpha` | พบภาพยนตร์ที่ตรงกับคำค้น | พบ 1 เรื่อง คือ Alpha Signal | PASSED |
| เพิ่มภาพยนตร์ซ้ำ | `watchlist add 101` สองครั้ง | เพิ่มเพียงครั้งเดียว | ครั้งที่สองแจ้งว่า "อยู่ในรายการรับชมแล้ว" | PASSED |
| อินพุตสิ้นสุด | EOF | ออกจากโปรแกรมอย่างสุภาพ | แสดงข้อความ "[สิ้นสุดอินพุต]" แล้วกล่าวอำลาก่อนออก | PASSED |

### 4.3 สรุปบทเรียน (Retrospective: Wow! & Whoops!)

**Wow! (ส่วนที่ทำได้ดี):** โค้ดถูกแยกส่วนติดต่อกับผู้ใช้ (CLI) ออกจากส่วนอื่นอย่างชัดเจน ทำให้อ่านและทดสอบได้ง่าย
การตรวจสอบอินพุตครอบคลุมทุกกรณีที่กำหนดไว้ใน Definition of Done และชุดทดสอบอัตโนมัติทั้ง 20 เคส
ก็จำลองอินพุตได้จริง ทำให้ข้อกำหนดทุกข้อพิสูจน์ซ้ำได้ด้วยคำสั่งเดียว

**Whoops! (ปัญหาและแนวทางแก้ไข):** ตอนแรก CLI ถูกออกแบบให้เป็นคำสั่งแบบครั้งเดียว (argparse)
แต่ Sprint 1 ต้องการเมนูแบบโต้ตอบพร้อมตรวจสอบอินพุต จึงต้องรีแฟกเตอร์ใหม่เป็นคลาส `CLI`
โดยแยกส่วนติดต่อกับผู้ใช้ออกมาให้ชัดเจน อีกจุดหนึ่งที่พบคือรายการรับชมยังเก็บไว้ในหน่วยความจำชั่วคราว
เมื่อปิดโปรแกรมแล้วข้อมูลจะหาย จึงวางแผนแก้ไขด้วยฐานข้อมูล SQLite ใน Sprint 3

### 4.4 ลิงก์และขั้นตอนถัดไป

- **Repository:** https://github.com/somjung/Movie-Discovery
- **Sprint ถัดไป (Sprint 2 — Back-End):** เชื่อมต่อ TMDB API จริง เก็บข้อมูลลงฐานข้อมูล SQLite พัฒนาฟังก์ชันค้นหา/กรอง/เรียงลำดับ และจัดการ File I/O
"""

FOOTER = """---

*หมายเหตุ: ข้อมูลภาพยนตร์ใน Sprint 1 เป็นข้อมูลตัวอย่างสำหรับสาธิตการทำงานของส่วนติดต่อกับผู้ใช้เท่านั้น
การเชื่อมต่อ TMDB API จริงจะเริ่มใน Sprint 2 (เมื่อเชื่อมต่อแล้ว โปรแกรมและเอกสารจะแสดงข้อความ
"This product uses the TMDB API but is not endorsed or certified by TMDB." ตามข้อกำหนดของ TMDB)*
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

PIP = '''# ติดตั้งไลบรารีที่ใช้ทดสอบ (ถ้ามีอยู่แล้วระบบจะข้ามให้)
%pip install -q pytest flake8
import pytest
print("pytest", pytest.__version__)
'''

DEMO = '''# สาธิตการใช้งานจริง: จำลองอินพุตเหมือนมีผู้ใช้พิมพ์คำสั่งทีละบรรทัด
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

EDGE = '''# ทดลองกรณีขอบเขตตาม Definition of Done (ผลลัพธ์จริงจากโปรแกรม)
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
        md(PITCH),
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
