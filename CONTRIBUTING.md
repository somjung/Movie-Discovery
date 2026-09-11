# Contributing

Course project workflow (team of 3).

## Branches

- `main` — always working; only tested work gets merged in
- `feature/<short-name>` — one feature or fix per branch

## Before pushing

1. Run the tests: `python -m pytest -q`
2. Run the linter: `flake8 src tests`
3. Keep commits small and message them clearly
   (e.g. `feat: add watchlist CSV export`)

## Pull requests

- One reviewer required (another team member)
- CI (GitHub Actions) must pass before merge
