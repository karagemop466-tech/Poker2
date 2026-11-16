# COORDINATION.md — Shared task board

Session ID: `a22d577b` · Branch: `arena/a22d577b-poker2` (base `058cd54` on `main`)

Status values: `unclaimed` · `in progress` · `done` · `needs review` (published on the Flagged for Review page; does not block).

| # | Task | Status | Owner (session) | File scope |
|---|------|--------|-----------------|-----------|
| T1 | Repo review + irregularity log | done | a22d577b | `COORDINATION.md`, `data/flags.json` |
| T2 | Single-entry tournament data — The Venetian (DeepStack Extravaganza IV, Nov 16–Dec 23 2026) | done | a22d577b | `data/tournaments.json` |
| T3 | Excluded / unverified tournament data — Wynn daily + WPT (official schedules) | done (WPT structure chunks 1–7 still unread; rows stay UNVERIFIED) | a22d577b | `data/tournaments.json` |
| T4 | Hotels: resort-fee verification (Venetian, Wynn) | done (room rates and walking times not verified) | a22d577b | `data/hotels.json` |
| T5 | Executive summary, questions, suggestions | done | a22d577b | `data/questions.json`, `data/suggestions.json`, `data/summary.json` |
| T6 | Site build (static HTML generator, link + verification checks) | done | a22d577b | `scripts/`, `*.html`, `assets/`, `.nojekyll` |
| T7 | Integration: re-verify combined data, build, PR, merge, Pages check | in progress | a22d577b | all shared outputs |

Scope note: this session is the only active session on the repo at the time of claiming. The shared outputs (`data/*.json`, site index/nav) are written by this session, so T7 is performed here as the integration step.

## Flags (session-level)

- **Branch naming deviation:** the task spec asks for `session-<id>/<task>`, but this session is assigned `arena/a22d577b-poker2`. The name was NOT changed (the branch name is fixed for this session). Recorded here and as flag F02 on the Flagged for Review page.
- **Coverage:** only The Venetian and Wynn Las Vegas. MGM Grand's official poker page returned "Page not found"; other Strip rooms not covered (flag F19).

## Log

- **2026-11-16 · a22d577b** — Claimed T1–T7 above. Repo contained only `README.md` ("# Poker2"); no COORDINATION.md existed, so it was created here. GitHub Pages is already enabled on `main` (legacy build, path `/`, `https://karagemop466-tech.github.io/Poker2/`).
- Coverage decision: research is limited to two Strip properties whose official poker and resort pages were reachable and read: **The Venetian** and **Wynn Las Vegas** (official Wynn poker page). Other Strip rooms are NOT covered in this pass and are listed as an open item.
- **2026-11-16 · a22d577b** — Committed `data/tournaments.json` (32 verified Venetian single-entry rows, 15 Venetian + 17 Wynn excluded, 17 Venetian + 49 Wynn WPT unverified). Added `data/hotels.json`, `flags.json` (20 items), `questions.json`, `suggestions.json`, `summary.json`, `sources.json`.
- **2026-11-16 · a22d577b** — Built the static site with `scripts/build.mjs` (11 pages, root landing page, assets, `.nojekyll`). The build fails if any row lacks an official-host source. Internal link check passed.
- **2026-11-16 · a22d577b** — Corrected drafts: removed unsupported claims (Wynn phone number, Encore location, invented WPT re-entry text, unverified aggregator figures). Checked that the constructed Venetian structure URL resolves (sheet 16 confirmed).
- **Conflicts:** none. No other session has touched the repo.
