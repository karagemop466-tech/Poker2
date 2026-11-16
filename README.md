# Vegas Poker Planner

A static, source-linked research dashboard for Las Vegas Strip-area poker tournaments and hotel planning. The first snapshot is dated 16 November 2026.

## Pages

- `index.html` — executive summary and provisional comparisons
- `tournaments.html` — selected dated events, buy-in/guarantee comparisons, and paid-extra-spend events kept separate
- `schedule.html` — a cautious start-time plan, including the lack of an official 8:00 AM tournament start
- `hotels.html` — source-verified fee information and clearly blank date-specific nightly totals
- `decision.html` — question/answer register and proposed improvements
- `flagged.html` — unverified facts and source irregularities
- `sources.html` — official source register and calculation rules

## Local preview

Open `index.html` in a browser, or run a static server from the repository root, e.g. `python3 -m http.server 8000`.

## Publication

GitHub Pages deployment is configured through `.github/workflows/pages.yml` on pushes to `main` and manual workflow dispatch. The repository's Pages setting must use **GitHub Actions** as its build/deployment source.

## Verification policy

Official venue/hotel sources are linked at the data row level. A blank means unverified/not published in the source checked, not zero. Tournament guarantee-to-buy-in ratios are descriptive arithmetic, not expected return. The research is a dated snapshot; check operator terms, event availability, hotel quotes and schedule changes again before travel.
