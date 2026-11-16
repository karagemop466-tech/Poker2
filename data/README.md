# Data fields and evidence rules

Research snapshot currently recorded as **2026-11-16 UTC**. That date describes the stored data review; it is not a claim that a daily schedule monitor has already run. The first scheduled monitor execution establishes URL baselines.

## Tournament records

`last_checked` records the source-review date attached to the current row. Every event row also has `rule_evidence` with four separate keys: `single_entry`, `re_entry`, `add_on`, and `fee`. Each evidence item contains `value`, `source_excerpt`, `retrieval_date`, `status`, and `source_urls`. Empty evidence fields are intentional: do not fill them from a tournament title or an event's “1Day” label. A value should be entered only with a verbatim official-source excerpt and the date it was retrieved. Current rule evidence remains unverified where those excerpts are not stored.

`schedule_fit` separates `late_registration_cutoff`, `finish_time`, `plausible_duration`, `overlap_status`, and `daily_role`. Missing finish/cutoff data means the site must not promise that entries can be played in sequence. `daily_role` remains unassigned until a date-specific itinerary can be supported.

## Hotel records

`rate_log` is an array, not a current single quoted value. It is empty until a dated official quote is captured. A future log entry should record:

- `retrieved_at` timestamp (UTC), official booking URL and source excerpt;
- check-in/check-out dates, occupancy, room category and cancellation deadline;
- checkout total, nightly average, room subtotal, mandatory resort fee, tax, parking, and any mandatory booking charge;
- conditional player-rate terms as a separate note, never silently treated as an unconditional discount.

Never calculate a true nightly cost without the exact stay's payable checkout total and required fee/tax detail. Do not apply a property's tax rate to another property's fees without an official basis.

Each hotel `walking_routes` array is a set of possible hotel–poker-room pairs. `walk_minutes`, `within_30_minutes`, provider, route URL, and `checked_at` are empty until the route is checked from official addresses; no straight-line distance is substituted for walking time.

## Official-source monitor

`data/sources.json` is the registry of official HTTPS pages and PDFs. The scheduled GitHub Actions workflow fetches the response body, compares SHA-256 hashes against the last successfully saved run, publishes the current report, and opens/comments on a source-review issue when a hash changes. A hash difference is only a review flag; dynamic content or a redesign may also cause it. Fetch errors retain the previous successful hash and are displayed as unavailable, not changed.

Run `python3 scripts/monitor_sources.py` to make a local report (network access is required). Run `python3 scripts/build_venues.py` to regenerate venue profiles and `python3 scripts/build_search_index.py` to refresh cross-page table search. The scheduled Pages workflow creates the live monitor report at runtime; no site row is silently edited based on a hash difference.
