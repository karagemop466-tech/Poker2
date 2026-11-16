# Vegas Poker Planner

A static, source-audited research dashboard for Las Vegas Strip poker tournament planning.
Every number on the site links to the official page, PDF or structure sheet it came from, and
every table row carries the date that source was last read. Values no official source states are
left blank and listed on the Flagged page — they are never inferred or filled in.

Live site: <https://karagemop466-tech.github.io/Poker2/>

## Rebuild

```bash
python3 scripts/poker_data.py        # dataset  -> data/poker/dataset.json
python3 scripts/build_dashboard.py   # pages    -> index.html, *.html, venues/*.html
python3 scripts/stamp_archive.py     # banners on every archived page
```

Both generators are deterministic: rebuilding without changing the data produces byte-identical
HTML, which is what makes a diff in a pull request meaningful.

## Where the numbers live

There is exactly one source of truth: `scripts/poker_data.py`. It holds

| Constant | Contains |
|---|---|
| `SOURCES` | every page/PDF/route read, keyed, with publisher, URL and what it was used for |
| `EVENTS` | 237 tournament rows (Venetian DSE IV, Wynn WPT, 20 recurring daily/weekly events) |
| `VENUES` | the six properties that run tournaments |
| `HOTELS` | seven properties with verified resort fees, taxes, parking, cancellation terms |
| `WALKS` | 14 measured hotel→poker-room walking pairs |
| `RATE_LOG` | dated rate observations, append-only |
| `FLAGS` | 13 source irregularities |
| `QUESTIONS` | 12 open questions, 5 of them blocking |
| `SUGGESTIONS` | 13 gated improvement proposals |

Nothing else in the repository may hold a buy-in, guarantee, fee, rate or walk time. If a page
needs a number, it imports it from here.

## Site structure

```
index.html          Dashboard — the verdict, the gaps, the top ratios
events.html         Every event, searchable, filterable, with per-row source + last-checked
ranking.html        Three lists: sheet-silent, spend-more, and non-comparable formats
dayplan.html        One primary event per date, plus conditional fallbacks
trip-cost.html      Calculator: entries × buy-ins + nights × true hotel cost
hotels.html         Fees, taxes, parking, cancellation — and the missing room rate
rates.html          Append-only rate log
walking.html        30-minute walking gate, measured
venues/             One page per property (6)
questions.html      What must be answered before booking
suggestions.html    Gated improvement proposals
flagged.html        Source irregularities, with severities
sources.html        Every source, classed by authority
repo-review.html    Line-by-line review of this repository itself
archive/            The four superseded dashboards, bannered and marked unusable
```

## The two rules the site is built to keep

**1. Silence is not confirmation.** `entry_rule = "not_stated"` is a distinct value from a
confirmed single-entry rule, and the site distinguishes three states per row:

- `silent on entry limit` — the event's own structure sheet was opened and says nothing about a
  maximum number of entries. 53 rows.
- `sheet not read` — nobody opened that event's sheet, so the row is *unverified*, not silent.
  168 rows.
- `re-entry` / `rebuy + add-on` — the property's own terms positively permit paying again. 16 rows.

No row carries a written single-entry confirmation, so the "single-entry confirmed" filter returns
zero rows by design. That is the finding, not a bug.

**2. A derived number is a number nobody published.** An intermediate draft computed event lengths
from a table of level counts written from memory. It was removed rather than corrected, and the
removal is recorded on `repo-review.html`. No event-length figure appears anywhere now.

## Publishing

`.github/workflows/pages.yml` publishes the repository root on push to `main` and on manual
dispatch. See `COORDINATION.md` for the session log, the verification record and the merge/deploy
trail.

Research snapshot: **2026-11-16 (UTC)**.
