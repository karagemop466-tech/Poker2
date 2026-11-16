# Vegas Poker Planner

A static, source-audited research dashboard for Las Vegas Strip poker tournament planning. The site separates verified official schedule facts from unknowns; it intentionally avoids inferring single-entry status, hotel rates, fees, and walking times.

## Preview locally

Open `index.html` directly, or run `python3 -m http.server 8000` and visit `http://localhost:8000`.

## Publishing

GitHub Pages workflow is configured to publish the repository root on pushes to `main` and via manual dispatch. Site: `index.html`.

## Verification notes

Research snapshot: 2026-11-16 (UTC). Primary schedule: [Venetian DeepStack Extravaganza IV official schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html). Series overview: [official Venetian tournament series](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html). Hotel promotion context: [official Venetian offers](https://www.venetianlasvegas.com/hotel/offers.html). Per-row links point directly to the published schedule; full structure sheets are linked from that source. No event is represented as confirmed single-entry until its official rules are checked.

See [COORDINATION.md](COORDINATION.md) for scope and verification log. Use the site's **Flagged for Review** section before relying on any unverified item.

## Decision tools and maintenance

- [Trip cost calculator](trip-cost.html): computes `entries × buy-in + nights × true hotel cost/night`. It intentionally starts blank; no trip dates or dated hotel quote were provided.
- [Venue directory](venues/index.html): separate profiles for Venetian, Wynn, Bellagio, MGM Grand, and ARIA; each groups known event leads and hotel context while preserving blanks.
- [Official source monitor](source-monitor.html): a GitHub Actions workflow re-fetches the URLs in `data/sources.json` daily at 07:00 UTC, flags changed response hashes for review, and publishes the report. First successful checks establish baselines; a hash change is not treated as proof that a listed fact changed.
- Shared search filters tables on the current page and searches indexed table rows site-wide. The tournament table also has a date selector and a strict confirmed-freezeout filter (currently no row is confirmed under the strict displayed standard).
- Tournament and hotel data carry `last_checked`, structured entry-rule evidence placeholders, schedule-fit status fields, and a dated hotel `rate_log`. Empty values remain unverified; no hotel quote, walking time, or event finish duration has been invented.

Regenerate new views with `python3 scripts/build_venues.py` and `python3 scripts/build_search_index.py`. See [data/README.md](data/README.md) for the source/evidence schema and automation behavior.

## Category pages (added)

Detail pages live in `pages/`: single-entry candidates, re-entry/spending events (kept separate), 8 AM schedule, hotel cost detail, summary, flagged rows, site-improvement suggestions (awaiting your choice; no changes made), questions, and repo review. Regenerate them with `python3 scripts/build.py`. Data lives in `data/`. Blank cells are unverified and are listed on the flagged pages.
