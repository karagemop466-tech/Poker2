# Vegas Poker Planner

A static, source-audited research dashboard for Las Vegas Strip poker tournament planning. The site separates verified official schedule facts from unknowns; it intentionally avoids inferring single-entry status, hotel rates, fees, and walking times.

## Preview locally

Open `index.html` directly, or run `python3 -m http.server 8000` and visit `http://localhost:8000`.

## Publishing

GitHub Pages workflow is configured to publish the repository root on pushes to `main` and via manual dispatch. Site: `index.html`.

## Verification notes

Research snapshot: 2026-11-16 (UTC). Primary schedule: [Venetian DeepStack Extravaganza IV official schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html). Series overview: [official Venetian tournament series](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html). Hotel promotion context: [official Venetian offers](https://www.venetianlasvegas.com/hotel/offers.html). Per-row links point directly to the published schedule; full structure sheets are linked from that source. No event is represented as confirmed single-entry until its official rules are checked.

See [COORDINATION.md](COORDINATION.md) for scope and verification log. Use the site's **Flagged for Review** section before relying on any unverified item.

## Category pages (added)

Detail pages live in `pages/`: single-entry candidates, re-entry/spending events (kept separate), 8 AM schedule, hotel cost detail, summary, flagged rows, site-improvement suggestions (awaiting your choice; no changes made), questions, and repo review. Regenerate them with `python3 scripts/build.py`. Data lives in `data/`. Blank cells are unverified and are listed on the flagged pages.

## Extended research view

The cross-venue evidence dashboard for the 2026 research snapshot is in [`site/index.html`](site/index.html); after this branch is merged, the existing root Pages workflow will serve it at `/Poker2/site/`. It incorporates official source checks for Caesars Palace, Horseshoe, Venetian, Wynn/WPT, Bellagio, MGM Grand, SAHARA, and hotel terms without replacing the existing root dashboard.
