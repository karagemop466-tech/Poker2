# Coordination — Poker2 (branch `arena/f1bedfe3-poker2`)

Shared task board for the Las Vegas Strip poker tournament + hotel research and GitHub Pages site.

## Session
- This session ID: `arena-poker-agent-1` (single active session)
- Branch: `arena/f1bedfe3-poker2` (branched from `058cd5412575dad64023c3d0d0f7e15d6815016a` of main)
- All work is committed to this branch per Arena session rules.

## Task board

| Task | Status | Owner | Files touched | Sources / verification |
|------|--------|-------|---------------|------------------------|
| T1: Research live upcoming poker tournaments near Las Vegas Strip (single-entry focus) | done | arena-poker-agent-1 | `pages/tournaments.html` | Venetian DSE IV official listing + structure sheets (venetianlasvegas.com), verified Nov 16, 2026; 47 single-flight events |
| T2: Separate section — tournaments where spending more buys an advantage (rebuys/add-ons/double bullets) | done | arena-poker-agent-1 | `pages/advantage-tournaments.html` | Wynn daily structure sheets (wynnresorts.com CDN), WPT World Championship schedule PDF (official), Venetian multi-flight listings |
| T3: Research hotels within 30-min walking distance of tournaments; true cost/night incl. resort fees | done | arena-poker-agent-1 | `pages/hotels.html` | Wynn + Venetian resort fees from official terms ($55+tax); others blank/flagged |
| T4: Build all-day tournament schedule (8 AM start, max entries) | done | arena-poker-agent-1 | `pages/schedule.html` | Derived from T1/T2; earliest verified start 10:10 AM (flagged gap) |
| T5: Executive summary | done | arena-poker-agent-1 | `pages/executive-summary.html` | T1–T4 |
| T6: Suggestions section (site improvements / decision-making) | done | arena-poker-agent-1 | `pages/suggestions.html` | — |
| T7: Questions / information / answers to resolve before decisions | done | arena-poker-agent-1 | `pages/questions.html` | Q1–Q13 |
| T8: Flagged for Review page (unverified items + irregularities) | done | arena-poker-agent-1 | `pages/flagged-review.html` | T1–T7 |
| T9: Landing page + navigation + dashboard-style tables | done | arena-poker-agent-1 | `index.html`, `assets/css/style.css`, `pages/*.html` | — |
| T10: Integration, line-by-line re-verification, build check, PR to main, GitHub Pages publish | in progress | arena-poker-agent-1 | All | See flagged-review.html for unverified items |

## Rules
- No task is marked verified without checking against an official source; source link recorded per row.
- Unverified values: left blank + flagged on the Flagged for Review page. Never inferred.
- Claim a task by writing your session ID + file scope, commit and push immediately.
- Small, frequent commits; `git pull --rebase` before every push.
- Shared outputs (index, nav, table data) are changed only by the final integration session.
