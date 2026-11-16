# Coordination — Poker2 (branch `arena/f1bedfe3-poker2`)

Shared task board for the Las Vegas Strip poker tournament + hotel research and GitHub Pages site.

## Session
- This session ID: `arena-poker-agent-1` (single active session)
- Branch: `arena/f1bedfe3-poker2` (branched from `058cd5412575dad64023c3d0d0f7e15d6815016a` of main)
- All work is committed to this branch per Arena session rules.

## Task board

| Task | Status | Owner | Files touched | Sources / verification |
|------|--------|-------|---------------|------------------------|
| T1: Research live upcoming poker tournaments near Las Vegas Strip (single-entry focus) | unclaimed | arena-poker-agent-1 | `data/tournaments.md`, `pages/tournaments.html` | Official casino poker room pages (linked per row) |
| T2: Separate section — tournaments where spending more buys an advantage (rebuys/add-ons/double bullets) | unclaimed | arena-poker-agent-1 | `pages/advantage-tournaments.html` | Official casino poker room pages |
| T3: Research hotels within 30-min walking distance of tournaments; true cost/night incl. resort fees | unclaimed | arena-poker-agent-1 | `data/hotels.md`, `pages/hotels.html` | Official hotel pages |
| T4: Build all-day tournament schedule (8 AM start, max entries) | unclaimed | arena-poker-agent-1 | `pages/schedule.html` | Derived from T1/T2 |
| T5: Executive summary | unclaimed | arena-poker-agent-1 | `pages/executive-summary.html` | T1–T4 |
| T6: Suggestions section (site improvements / decision-making) | unclaimed | arena-poker-agent-1 | `pages/suggestions.html` | — |
| T7: Questions / information / answers to resolve before decisions | unclaimed | arena-poker-agent-1 | `pages/questions.html` | — |
| T8: Flagged for Review page (unverified items + irregularities) | unclaimed | arena-poker-agent-1 | `pages/flagged-review.html` | — |
| T9: Landing page + navigation + dashboard-style tables | unclaimed | arena-poker-agent-1 | `index.html`, `assets/*`, `pages/*.html` | — |
| T10: Integration, line-by-line re-verification, build check, PR to main, GitHub Pages publish | unclaimed | arena-poker-agent-1 | All | — |

## Rules
- No task is marked verified without checking against an official source; source link recorded per row.
- Unverified values: left blank + flagged on the Flagged for Review page. Never inferred.
- Claim a task by writing your session ID + file scope, commit and push immediately.
- Small, frequent commits; `git pull --rebase` before every push.
- Shared outputs (index, nav, table data) are changed only by the final integration session.
