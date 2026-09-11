# Movie Discovery & Watchlist Builder

Final term project for **CP352301 Script Programming (1/2569)** — a command-line
Python application that finds movies similar to what you like, filters and
ranks the results, keeps a personal watchlist, and exports it to CSV.

> This product uses the TMDB API but is not endorsed or certified by TMDB.

## Sprint status

- **Sprint 1 (Front-End App Dev) — COMPLETE.** Interactive CLI: welcome
  banner, command menu, input handling (`.strip().lower()`), full input
  validation, and graceful exits. Demonstrated with the built-in sample
  dataset; spec + Definition of Done in `PLAN.md`.
- **Sprint 2 — Back-End (next).** TMDB API client, SQLite persistence, and
  the search/filter/rank logic — foundation modules are already prepared in
  `src/` with their test-suite (they will be presented in Sprint 2).
- Sprint 3 — Full-stack integration. Final — DevOps/CI/CD + AI.

## Team & roles

| Role | Member |
|---|---|
| Planner / Team Leader | _(to be added)_ |
| Coder | อเสข ปัญญาวงค์ (Asek Panyawong) |
| Debugger / QA | _(to be added)_ |

## Sprint 1 features (CLI)

- Commands: `search <title>` · `discover <id>` · `watchlist add|list|clear` ·
  `help` · `quit` / `exit` / `q` / `ออก`
- Case-insensitive and whitespace-tolerant commands (`.strip().lower()`)
- Input validation with friendly warnings — the program never crashes
  (`try / except ValueError`, EOF and Ctrl+C handled gracefully)
- Edge cases covered by automated tests + scripted sessions (see `PLAN.md`)

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
python -m src.app               # start the interactive CLI
```

## Sprint 1 submission notebook (Colab)

The full Sprint 1 report (project pitch, plan, execution and results) is in
`notebooks/Sprint1_MovieDiscovery.ipynb`. To re-run it: upload the file to
Google Colab and click **Run all**. It works end-to-end with the built-in
sample data (no API key required).

## Project structure

```
script-final-project/
├── PLAN.md              # Sprint 1 spec + Definition of Done (Planner artifact)
├── src/
│   ├── app.py           # entry point (python -m src.app)
│   ├── cli.py           # interactive front-end (Sprint 1)
│   ├── sample_data.py   # built-in demo dataset (until the Sprint 2 API arrives)
│   ├── tmdb_client.py   # [Sprint 2] TMDB API client with error handling
│   ├── movie_store.py   # [Sprint 2] SQLite persistence layer
│   ├── discovery.py     # [Sprint 2] dedupe -> filter -> rank logic
│   ├── watchlist.py     # [Sprint 2] Top-N watchlist builder
│   ├── exporter.py      # [Sprint 2] CSV export
│   └── config.py        # constants + API-key lookup
├── tests/               # pytest suite (CLI + foundation modules)
├── data/                # local SQLite file (created in later sprints)
├── notebooks/           # Sprint 1 submission notebook (pitch / plan / execution / result)
├── tools/               # notebook rebuild helper (build_notebook.py)
└── .github/workflows/   # CI: flake8 + pytest on every push
```

## Testing & code quality

```bash
python -m pytest -q      # unit tests — no network needed
flake8 src tests         # style check (PEP 8)
```

CI: `.github/workflows/ci.yml` runs flake8 and pytest on every push
(GitHub Actions).

## Roadmap

- [x] Sprint 1 — Front-end CLI foundation (this sprint)
- [ ] Sprint 2 — Back-end: real TMDB data, SQLite, search/filter/rank
- [ ] Sprint 3 — Full-stack integration + edge-case hardening
- [ ] Final — DevOps, CI/CD & AI features, complete documentation, demo

## License

MIT — see [LICENSE](LICENSE).
