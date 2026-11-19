# Live official-source verification sweep — arena/2e732aa2-poker2, 2026-11-19

Method: every page below was fetched and read in full through the platform page-fetch tool
on 2026-11-19 (UTC). Nothing was inferred; each result records what the page printed today.
The structured schedule comparison was done programmatically against the committed
transcriptions; the row-level artifact is
`research/2e732aa2-live-dse-nov-2026-rows-2026-11-19.json` (94 rows, transcribed verbatim
from the four fetched chunks of the schedule page).

## 1. Venetian DeepStack Extravaganza IV schedule page — UNCHANGED (94/94 rows)

Source: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
(4/4 content chunks fetched 2026-11-19; heading "DeepStack Extravaganza IV — November 16 –
December 23, 2026 — More than $3.6 Million in guaranteed tournament prize pools").

* All 94 printed schedule rows (incl. flights and Day-2 restarts) were transcribed from the
  fetched chunks and diffed against the committed transcriptions:
  * `/plan/` surface (`site-data/events.json`, 94 rows): **zero missing, zero extra, zero
    mismatches** on (date, start time, event number, structure-sheet number). The 16 name
    "differences" are subtitle punctuation/abbreviation only (e.g. page prints
    "Must be 50+ years of age to participate", dataset abbreviates "must be 50+ years of
    age"; page "Event # 39" vs dataset "Event #39"); no value differs.
  * root surface (`data/master.json`, 83 non-restart Venetian rows): **all 83 rows match**
    on (date, start time, event number, structure-sheet URL). Buy-in in every row equals the
    dollar amount printed in the live event name; every GTD printed in a name equals the
    stored `gtd` ($10K/$8K/$15K/$30K/$20K/$40K/$25K/$50K/$75K/$150K/$300K/$500K/$1 Mill).
    The 11 rows on the page that master.json does not list are all "Day 2 Restart" /
    "Final Table" continuation rows — by design, not entries you can buy into.
* Conclusion: the official schedule is unchanged in every value the site publishes as of
  2026-11-19. Root-surface Venetian rows' `last_checked`/`schedule_checked` advanced to
  2026-11-19 by the overlay in `scripts/build_master.py` (schedule page only — the 37
  structure sheets were NOT re-read today, so `struct_checked`/`sheet_retrieved` are NOT
  advanced).

## 2. Venetian DeepStack series overview — unchanged since the 027412f0 re-read

Source: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html
(2026-11-19). Confirms exactly what `master.json.verification_027412f0` recorded:
Current Series DSE IV Nov 16–Dec 23 2026 (>$3.6M GTD) with the five headline events
($800 NLH $500K GTD Dec 3–6; $2,200 PokerAtlas Championship Title Event $1M GTD Dec 12–14,
final table streamed Dec 14 12pm; $1,100 Seniors $300K GTD Dec 13–15, 50+; $1,100 NLH $500K
GTD Dec 17–20; $600 NLH $150K GTD Dec 20–23); **Next Series DeepStack Extravaganza NYE
Dec 24 2026 – Jan 10 2027 (>$1.1M GTD)** with $2,200 NLH $300K GTD Dec 27–31 (Ante Up
Championship, streamed Dec 31 11am) and $1,600 NLH MSPT $400K GTD Jan 1–4. No further change.

## 3. Venetian resort-fee page — UNCHANGED ($55 plus tax)

Source: https://www.venetianlasvegas.com/resort/resort-fee.html (2026-11-19).
Verbatim: "Rates include a daily Resort Fee of $55 plus tax per night, payable upon
check-in." Inclusions unchanged (Canyon Ranch access for two, in-suite internet,
boarding-pass printing, unlimited local/toll-free calls, PressReader). Matches the
published `$55` fee and its excerpt.

## 4. Venetian poker suite-rate page — UNCHANGED ($119 / $209 starting rates)

Source: https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html (2026-11-19).
Verbatim confirms every published condition: "start as low as $119 and $209 and can be
higher"; single/double occupancy in a Luxury King Suite in The Venetian or The Palazzo;
"$55 resort fee per night stayed"; qualification = six hours of active live cash gameplay
OR buy-in to a $300-or-higher tournament per night stayed, met before 2 a.m. the last night
stayed; otherwise the nightly rate reverts to the prevailing rate; book by phone with code
EPOKR25; rates out to 150 days maximum. The page still does not attribute $119 vs $209 to a
specific tower, so the dataset's refusal to map the amounts to Venetian vs Palazzo remains
correct.

## 5. Wynn poker room page — unchanged at page level

Source: https://www.wynnlasvegas.com/casino/poker (2026-11-19).
* "WPT WORLD CHAMPIONSHIP — November 27–December 21" with schedule/structures PDFs at the
  same CDN URLs already cited by the Wynn rows; "New for 2026, the Super Gold Million
  brings a $400 buy-in featuring a $3,000,000 guarantee!" — matches the published Wynn data.
* "WYNN SIGNATURE SERIES — January 11–24, 2027" (schedule + structures PDFs) — future
  series, noted for coverage, not transcribed into the dataset (outside the current trip
  window and not yet row-level verified; structures PDF URL was posted
  v1762299460 — see Flagged note).
* Daily tournaments section re-states: twice daily during non-event timeframes,
  $200,000 weekly guarantee total, "$40,000 guaranteed NLH Rebuy on Friday", "$10,000
  guaranteed event every evening at 6 p.m.", and "the Daily Tournament schedule will be
  suspended during each Wynn Signature, Wynn Millions, and Classic tournament series" —
  consistent with the published Wynn classification (dailies separate from strict
  freezeouts; WPT events allow re-entry per the structures PDF read 2026-11-17).
* No Wynn row dates were advanced: the row-level source documents (WPT schedule PDF, daily
  poster PDF, structures PDF) were not re-read today; only the page-level facts above were
  confirmed.

## 6. Source monitor state (workflow-owned)

* The scheduled monitor (`source-monitor.yml`, daily 15:00 UTC) had not run at sweep time
  (last run 2026-11-18; the 2026-11-19 repair left 14 baselines "re-check pending under
  normalized fingerprint"). `gh workflow run` is not permitted to this integration token
  (HTTP 403), and the sandbox has no egress to casino domains, so the re-check could not be
  executed locally either — `scripts/monitor.py --dry-run` correctly reported
  "0 of 87 URLs were readable — nothing written, no run recorded" and left state untouched.
* The next scheduled run (15:00 UTC 2026-11-19) will resolve the pending baselines with
  real fetches under the normalized fingerprint; unchanged fetches clear them per
  `monitor.py` (a pending change is only cleared by an identical later fetch plus manual
  review).
* The 87-URL registry itself was regenerated from master.json citations today and is
  byte-identical apart from unicode-escape style (reverted; no content change).

## Values changed by this sweep

None. Every value read from an official page today matches what the site already publishes.
The only data change is the honest advancement of the Venetian rows' verification dates
(`last_checked`, `schedule_checked` → 2026-11-19) plus a `verification_2e732aa2` record on
master.json, both via `scripts/build_master.py`.
