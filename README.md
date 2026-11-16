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

The repository's existing GitHub Pages configuration serves the repository root from `main` (branch deployment). The site is published by merging the static files to `main`; the current published Pages URL is `https://karagemop466-tech.github.io/Poker2/`. No Actions deployment workflow is used because the repository's Pages source is configured for branch deployment.

## Verification policy

Official venue/hotel sources are linked at the data row level. A blank means unverified/not published in the source checked, not zero. Tournament guarantee-to-buy-in ratios are descriptive arithmetic, not expected return. The research is a dated snapshot; check operator terms, event availability, hotel quotes and schedule changes again before travel.
