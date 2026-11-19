# arena/68b54771-poker2 — live official-source re-reads (2026-11-19, ~11:20 UTC)

Final-integration session re-reads. The board shows five other sessions performed full official
verification sweeps earlier today (PRs #96, #100, #101, #106, #107; most recently 2e732aa2 at
~11:10 UTC with 94/94 Venetian rows unchanged). This pass re-opens the decision-critical URLs
independently to confirm nothing changed on the pages in the interval, immediately before the
final integration merge. Tool: agent page-fetch (bash sandbox has no route to these hosts).

| # | URL (official) | Read | Result vs stored dataset |
|---|---|---|---|
| 1 | https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html | 2026-11-19 ~11:20 UTC | Chunk 1 of 4 read in full. Title: "DeepStack Extravaganza IV — November 16 – December 23, 2026", "More than $3.6 Million in guaranteed tournament prize pools". Printed rows through Nov 28 match the stored schedule exactly: Event 1 flights 1A–1D ($300, $75K GTD, 11:10 AM/5:10 PM, structures 10/9), Event 2 $300 1-Day $10K GTD Nov 18 11:10 AM (structure 5), Events 3–5 $200 RaceDay Stack 10:10 AM (structure 18), Event 6 $200 1-Day Nov 22 11:10 AM (structure 29), Events 7 1A/1B $400 $75K GTD (structure 2), Events 8–9 $200 PKO/Bounty $8K GTD 5:10 PM (structures 30/1), Event 10 $400 $15K GTD Nov 25 11:10 AM (structure 6), Events 11–13 $200 Bounty 5:10 PM, Event 14 $600 $30K GTD Nov 27 (structure 7), Event 16 $600 Bounty $30K GTD (structure 11), Event 17 $400 PLO Bounty (structure 26). No event added, removed, retimed or renamed in the read portion. A full 4-chunk read at ~11:10 UTC today by arena/2e732aa2 found 94/94 rows unchanged (recorded on the board); this read corroborates it. |
| 2 | https://www.wynnlasvegas.com/casino/poker | 2026-11-19 ~11:20 UTC | Full page read. WPT World Championship November 27–December 21, 2026; Super Gold Million $400 buy-in / $3,000,000 guarantee (matches stored X-WPT06); Wynn Signature Series January 11–24, 2027; "Daily Tournament schedule will be suspended during each Wynn Signature, Wynn Millions, and Classic tournament series"; daily slate: "$40,000 guaranteed NLH Rebuy on Friday and a $10,000 guaranteed event every evening at 6 p.m." — all match the stored Wynn rows and rules. No change. |
| 3 | https://www.venetianlasvegas.com/resort/resort-fee.html | 2026-11-19 ~11:20 UTC | Full page read. "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in" with the standard inclusions list. Matches the stored Venetian/Palazzo resort fee ($55 + tax). No change. |
| 4 | https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip | 2026-11-19 ~11:20 UTC | Chunk 1 of 3 read. Caesars Palace poker room described as 16 tables on the Appian Way promenade, open 24/7 with a daily tournament slate; Horseshoe Hall of Fame Poker Room open around the clock; minimum age 21. Consistent with the stored guide excerpt and the VR-028 flyer-vs-guide conflict already recorded from the live reads today (arena/9e862af8, PR #100). No new discrepancy found in the read portion. |
| 5 | https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:7436500e-cac4-420a-b23a-02d3fec69900/original/as/room-tax-increase-transient-lodging-letter-111616.pdf | 2026-11-19 (re-read by arena/2c7e846d earlier today, recorded via PR #98/#102) | 13.38% Primary Gaming Corridor rate adopted by county notice. Not re-fetched again this session; the county's current rate table has still not been reached live — this remains flag F-07 (dated source, consistent but old). |

## Conclusion

No value changed on any page re-read this session. Nothing to re-date beyond what the row-owning
sessions already recorded today. The integration merge can proceed on the current data; the
scheduled monitor (`.github/workflows/recheck.yml`, 77 URLs, daily 15:00 UTC / 7 a.m. Las Vegas)
remains the ongoing change-detection mechanism, and its pending-review state is unchanged.

## Still open (unchanged, non-blocking, published on the Flagged for Review page)

- No official document anywhere states a single-entry/no-re-entry/no-add-on rule for any listed
  event (F-01); the confirmed-only filter legitimately returns zero rows and the site says so.
- Tournament finish times are unpublished; the day plan remains "one primary + conditional
  fallback, never an impossible sequence" and claims no verified end times (F-04/F-05).
- Exact-stay itemized hotel checkout quotes are not obtainable from the official booking engines
  without a browser session; the calculator treats missing lodging as unavailable, never $0.
- Walking times remain OSM/OSRM + Google-Maps-estimate pairs, not measured door-to-seat durations.
- The 2016 Clark County notice (13.38%) is dated; the county's current rate table was not reachable.
