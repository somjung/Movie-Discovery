# สถาปัตยกรรมระบบ — Sprint 2: Back-End App Dev

ระบบค้นพบภาพยนตร์และสร้างรายการรับชม · CP352301 Script Programming (1/2569)

เอกสารสรุปสถาปัตยกรรมของระบบหลังปิดงาน Sprint 2 (Back-End) ใช้เป็นแหล่งอ้างอิงของรายงานและการนำเสนอ ประกอบด้วยการแบ่งชั้นสถาปัตยกรรม หลักฐานการตรวจเชิงกลไก และแผนภาพคลาส UML

## 1. การแบ่งชั้นสถาปัตยกรรม (Layer Separation)

ระบบแยกเป็น 3 ชั้นตามคู่มือรายวิชา (Separation of Concerns) โดยเทียบกับสไลด์โครงสร้างโปรเจกต์ของ Sprint 1 — สถานะที่ระบุว่าเป็นงาน Sprint 2 ปิดครบแล้วในรอบนี้ (ตรวจจากโค้ดจริงใน src/ ทั้ง 9 โมดูล):

```
┌────────────────┬─────────────────────────────────┬────────────┐
│ Layer          │ Modules                         │ Status     │
├────────────────┼─────────────────────────────────┼────────────┤
│ Presentation   │ app.py · cli.py                 │ delivered  │
│ Business Logic │ discovery.py · watchlist.py     │ delivered  │
│ Data Access    │ tmdb_client.py · movie_store.py │ delivered  │
│ Data Access    │ exporter.py (CSV export)        │ delivered  │
│ Fixtures       │ sample_data.py                  │ tests only │
│ Shared         │ config.py                       │ all layers │
└────────────────┴─────────────────────────────────┴────────────┘
```

- **ชั้นนำเสนอ (Presentation Layer)** — รับคำสั่ง ตรวจสอบอินพุต เรียกบริการ แล้วแสดงผลเป็นข้อความไทย ไม่มีตรรกะการคัดเลือกหรือจัดอันดับอยู่ในชั้นนี้
- **ชั้นตรรกะธุรกิจ (Business Logic Layer)** — ค้นหา/กรอง/เรียง/ตัดซ้ำ (DiscoveryService) และเพิ่มรายการ พร้อมดึงข้อมูลอัตโนมัติ (WatchlistBuilder) ทั้งสองคลาสรับ TmdbClient และ MovieStore ผ่านพารามิเตอร์ (constructor injection) จึงไม่ต้อง import ไฟล์ชั้นข้อมูลเลย
- **ชั้นเข้าถึงข้อมูล (Data Access Layer)** — TMDB API พร้อมแคช 24 ชั่วโมง (TmdbClient) · SQLite 6 ตาราง (MovieStore) · ส่งออก CSV (Exporter)
- **config.py** — ค่าตั้งต้นกลาง (ฐาน URL · timeout · คีย์ API · พาธไฟล์) ใช้ร่วมทุกชั้น และ **sample_data.py** — ชุดข้อมูลจำลองสำหรับเทสต์ออฟไลน์เท่านั้น

## 2. ทิศทางการพึ่งพาระหว่างชั้น

ลูกศรทุกเส้นชี้ลงล่างเท่านั้น — ชั้นล่างไม่รู้จักชั้นบน โค้ดจึงทดสอบและสลับของจริง/ของจำลองได้อย่างอิสระ:

```
┌────────────────────────────────────────────────────────────────┐
│                       PRESENTATION LAYER                       │
├────────────────────────────────────────────────────────────────┤
│ app.py    — entry point: main()                                │
│ cli.py    — CLI: menu · input validation · Thai messages       │
└────────────────────────────────────────────────────────────────┘
                                 │  composes services (downward)
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                      │
├────────────────────────────────────────────────────────────────┤
│ discovery.py — DiscoveryService: search, filter, sort, dedupe  │
│ watchlist.py — WatchlistBuilder: ensure, add, favorites        │
└────────────────────────────────────────────────────────────────┘
                                 │  uses (constructor injection)
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                       DATA ACCESS LAYER                        │
├────────────────────────────────────────────────────────────────┤
│ tmdb_client.py  TmdbClient — TMDB API + 24 h cache             │
│ movie_store.py  MovieStore — SQLite (6 tables)                 │
│ exporter.py     Exporter — CSV export                          │
│ sample_data.py  offline test fixtures only                     │
└────────────────────────────────────────────────────────────────┘

           ▼                     ▼                     ▼
     TMDB REST API        data/movies.db          data/*.csv
      (requests)             (sqlite3)           (csv module)

config.py — shared by all layers (API key · paths)
```

*ภาพที่ 1 — โครงสร้าง 3 ชั้นและทิศทางการพึ่งพา*

ตรวจด้วยสคริปต์วิเคราะห์การ import ของทั้ง 9 โมดูล กฎ 6 ข้อ ผ่านครบโดยไม่มีการพึ่งพาสวนทาง:

```
┌───────────────────────────────────────────────┬─────────┐
│ Mechanical check                              │ Result  │
├───────────────────────────────────────────────┼─────────┤
│ R1 — nothing below presentation imports it    │ PASS    │
│ R2 — business imports no presentation/data    │ PASS    │
│ R3 — data imports nothing above it            │ PASS    │
│ R4 — requests used only in tmdb_client        │ PASS    │
│ R5 — sqlite3 / csv / json in the right module │ PASS    │
│ R6 — no import cycles (9 modules)             │ PASS    │
│ Total individual checks                       │ 51 / 51 │
└───────────────────────────────────────────────┴─────────┘
```

## 3. แผนภาพคลาส (UML Class Diagram)

คลาสหลัก 6 คลาสของระบบและความสัมพันธ์ (อ่านคู่กับตารางความสัมพันธ์ด้านล่าง):

```
                  ┌────────────────────────────┐
                  │           app.py           │
                  ├────────────────────────────┤
                  │ main() — program entry     │
                  └────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                              CLI                               │
├────────────────────────────────────────────────────────────────┤
│ input_func · output_func · data_dir · running                  │
│ store : MovieStore          client : TmdbClient | None         │
│ discovery : DiscoveryService   builder : WatchlistBuilder      │
├────────────────────────────────────────────────────────────────┤
│ run() · handle_command() · get_command_input()                 │
│ display_menu() · cmd_search() · cmd_discover()                 │
│ cmd_watchlist() · cmd_favorites() · cmd_export()               │
│ cmd_history() · cmd_help() · show_list()                       │
│ add_to_list() · remove_from_list()                             │
│ parse_discover_options() · parse_positive_int()                │
│ describe_tmdb_error() · format_movie()                         │
└────────────────────────────────────────────────────────────────┘
              │                                    │
              ▼                                    ▼
┌───────────────────────────┐        ┌───────────────────────────┐
│      DiscoveryService     │        │      WatchlistBuilder     │
├───────────────────────────┤        ├───────────────────────────┤
│ client : TmdbClient       │        │ store : MovieStore        │
│ store : MovieStore        │        │ client : TmdbClient       │
├───────────────────────────┤        ├───────────────────────────┤
│ search()                  │        │ ensure_movie()            │
│ find_similar()            │        │ add() · add_favorite()    │
│ SORT_OPTIONS              │        │ build()                   │
└───────────────────────────┘        └───────────────────────────┘
              │                                    │
              ▼                                    ▼
┌───────────────────────────┐        ┌───────────────────────────┐
│         TmdbClient        │        │         MovieStore        │
├───────────────────────────┤        ├───────────────────────────┤
│ api_key · session         │        │ db_path · connection      │
│ store : MovieStore | None │        │ CACHE_TTL_SECONDS         │
│ cache_ttl · hits/misses   │        ├───────────────────────────┤
├───────────────────────────┤        │ add_movie() · get_movie() │
│ search_movies()           │─cache─▶│ add_similar_link()        │
│ get_movie_details()       │        │ watchlist CRUD (4 ops)    │
│ get_similar()             │        │ favorites CRUD (4 ops)    │
│ get_recommendations()     │        │ record_search() · history │
│ _get() — cache/HTTP       │        │ cache get/save (24 h TTL) │
└───────────────────────────┘        └───────────────────────────┘

              ▼                                    ▼
        TMDB REST API                       data/movies.db
         (requests)                            (sqlite3)

Exporter — static utility: export_watchlist() · export_favorites()
  called by CLI · reads MovieStore rows · writes data/*.csv (csv module)
config.py (shared) — get_api_key() · get_db_path() · get_data_dir()
TmdbError · ExportError — raised in the data layer; CLI turns them into Thai messages
```

*ภาพที่ 2 — UML Class Diagram ของระบบหลัง Sprint 2*

```
┌──────────────────┬──────────────────┬─────────────────┬──────────────────────────────────────────┐
│ From             │ To               │ Relation        │ Detail                                   │
├──────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────┤
│ app.py           │ CLI              │ creates         │ main() starts the loop                   │
│ CLI              │ DiscoveryService │ composes 1      │ built in __init__ (None without API key) │
│ CLI              │ WatchlistBuilder │ composes 1      │ built in __init__                        │
│ CLI              │ TmdbClient       │ builds/receives │ from TMDB_API_KEY; injectable            │
│ CLI              │ MovieStore       │ builds/receives │ data/movies.db; injectable               │
│ CLI              │ Exporter         │ calls (static)  │ export command → CSV under data/         │
│ DiscoveryService │ TmdbClient       │ uses            │ search · similar · recommendations       │
│ DiscoveryService │ MovieStore       │ uses            │ saves kept movies, links, search log     │
│ WatchlistBuilder │ TmdbClient       │ uses            │ fetch details when the id is unknown     │
│ WatchlistBuilder │ MovieStore       │ uses            │ watchlist/favorites rows + movies        │
│ TmdbClient       │ MovieStore       │ uses 0..1       │ optional cache read/write (24 h TTL)     │
│ Exporter         │ MovieStore       │ reads           │ watchlist/favorites rows for CSV         │
│ CLI              │ config           │ uses            │ get_db_path() · get_data_dir()           │
│ TmdbClient       │ config           │ uses            │ base URL · timeout · API key             │
└──────────────────┴──────────────────┴─────────────────┴──────────────────────────────────────────┘
```

## 4. หมายเหตุการออกแบบ (Design Notes)

- ทั้งสองคลาสธุรกิจใช้ทั้ง TmdbClient และ MovieStore ผ่านพารามิเตอร์ฉีด — ลูกศรคู่ตรงในภาพคือคู่การใช้งานหลัก สลับคู่กันได้โดยไม่ต้องแก้โค้ด (เทสต์ทั้งชุดใช้ของจำลอง)
- TmdbClient กับ MovieStore มีความสัมพันธ์แบบมีเงื่อนไข (0..1): เปิดใช้แคชเมื่อมี MovieStore ส่งเข้ามา — ไม่ส่งก็ยังทำงานได้ตามพฤติกรรมเดิม
- CLI เรียก Exporter โดยตรง — Exporter เป็นยูทิลิตี้ ไม่มีสถานะ (stateless) ไม่มีตรรกะธุรกิจอยู่ในชั้นนำเสนอ
- ข้อผิดพลาดจากชั้นข้อมูล (TmdbError · ExportError) ถูกแปลงเป็นข้อความไทยที่ CLI — โปรแกรมไม่หยุดทำงาน
