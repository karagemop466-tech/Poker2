# COORDINATION.md — Shared task board

Session ID: `a22d577b` · Branch: `arena/a22d577b-poker2` (base `058cd54` on `main`)

Status values: `unclaimed` · `in progress` · `done` · `needs review` (published on the Flagged for Review page; does not block).

| # | Task | Status | Owner (session) | File scope |
|---|------|--------|-----------------|-----------|
| T1 | Repo review + irregularity log | in progress | a22d577b | `COORDINATION.md`, `data/flags.json` |
| T2 | Single-entry tournament data — The Venetian (DeepStack Extravaganza IV, Nov 16–Dec 23 2026) | in progress | a22d577b | `data/tournaments.json` |
| T3 | Excluded / unverified tournament data — Wynn daily + WPT (official schedules) | in progress | a22d577b | `data/tournaments.json` |
| T4 | Hotels: resort-fee verification (Venetian, Wynn) | in progress | a22d577b | `data/hotels.json` |
| T5 | Executive summary, questions, suggestions | in progress | a22d577b | `data/questions.json`, `data/suggestions.json`, `data/summary.json` |
| T6 | Site build (static HTML generator, link + verification checks) | in progress | a22d577b | `scripts/`, `*.html`, `assets/`, `.nojekyll` |
| T7 | Integration: re-verify combined data, build, PR, merge, Pages check | unclaimed | — | all shared outputs |

Scope note: this session is the only active session on the repo at the time of claiming. The shared outputs (`data/*.json`, site index/nav) are written by this session, so T7 is performed here as the integration step.

## Log

- **2026-11-16 · a22d577b** — Claimed T1–T7 above. Repo contained only `README.md` ("# Poker2"); no COORDINATION.md existed, so it was created here. GitHub Pages is already enabled on `main` (legacy build, path `/`, `https://karagemop466-tech.github.io/Poker2/`).
- Coverage decision: research is limited to two Strip properties whose official poker and resort pages were reachable and read: **The Venetian** and **Wynn Las Vegas** (poker room in Encore at Wynn). Other Strip rooms are NOT covered in this pass and are listed as an open item.
