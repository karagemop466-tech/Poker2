# COORDINATION.md — Shared task board

Owner session: `acd81e67` (branch `arena/acd81e67-poker2`, base `058cd54`).
This session is the only active agent on this repo. All work is on the branch above; the
`session-<id>/<task>` branch scheme in the original brief is replaced by the single branch
assigned to this session by Arena.

Status values: `unclaimed` · `in progress` · `done` · `needs review`
Items marked `needs review` are published on `/flagged.html` and do not block anything.

| ID | Task | Status | Owner | Files / scope |
|----|------|--------|-------|---------------|
| T1 | Repo review (line-by-line, sources, irregularities) | done | acd81e67 | `docs/repo-review.html`, `docs/flagged.html` |
| T2 | Single-entry live tournament research (Venetian DeepStack IV, Nov 16 – Dec 23 2026) | done (with flags; re-verified row-by-row against official schedule page on 2026-11-16) | acd81e67 | `data/tournaments.json`, `docs/single-entry.html`, `docs/schedule.html` |
| T3 | Re-entry / add-on / multi-flight / excluded tournaments | done (with flags) | acd81e67 | `docs/excluded.html` |
| T4 | Hotel research (official resort fees, addresses, rates) | done — rates & walking distance NOT verifiable from official sources | acd81e67 | `data/hotels.json`, `docs/hotels.html` |
| T5 | Site build (GitHub Pages, `docs/`) | done (built; deploy check after merge) | acd81e67 | `docs/*`, `scripts/build_site.py`, `docs/assets/*` |
| T6 | Verification pass + broken-link check | done (130/130 data rows have an https source; 0 broken internal links) | acd81e67 | `scripts/check_links.py` |
| T7 | Integration: PR `arena/acd81e67-poker2` → `main`, merge, Pages deploy check | in progress | acd81e67 | — |

## Task log (corrected 2026-11-16)
- Source of truth: official Venetian schedule page (`dse-nov-2026.html`), read in full; every Venetian row is taken from that table. Structure PDF numbers come from the same table.
- Earlier drafts contained registration-close times, a few structure numbers and two URLs that had not been read in this session. Those were removed; they are not in the published data.
- Rows left blank and flagged: Caesars resort fee and address, Wynn resort-fee link, all hotel nightly rates, Clark County room tax, walking times, Golden Nugget buy-in, Horseshoe times, Wynn WPT schedule (HTTP 502), MGM time mismatch (flag F-03).
- Hotels: no hotel is fully verified. Only resort fees are official (Venetian $55 + tax; Wynn $55 + tax, link pending).
- Irregularities: see `docs/flagged.html` (F-01 … F-22).

## Integration result (T7)
- PR: (to be recorded after creation)
- Merge result: (to be recorded)
- Pages deploy: (to be recorded)
