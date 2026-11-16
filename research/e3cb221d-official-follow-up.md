# Official-source follow-up audit — session `e3cb221d`

**Checked:** 2026-11-16 UTC. **Purpose:** New, source-checked facts that surfaced after the live dashboard and its other workstreams were already merged to `main`. This report is a handoff for the existing integration owner; it does not replace or modify another session's owned pages or datasets.

## Findings verified directly from official sources

### Wynn WPT World Championship structure terms
Source: [Wynn official WPT World Championship structures PDF](https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf). Calendar: [Wynn official poker page](https://www.wynnlasvegas.com/casino/poker) and [WPT schedule PDF](https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf).

- **$600 NLH, $400,000 guarantee:** Day 1A–1F are scheduled Nov 27–29, 2026; Day 2 Nov 30. The event-specific terms state **unlimited re-entry for each starting flight until the start of level 9**. A player who advances to Day 2 may not enter a later starting flight. Published entry fee split: $510 tournament prize pool + $65 tournament fee + $25 staff service charge = $600. This is not a strict single-entry event; keep it in a separate re-entry/spend-more category.
- **$800 NLH, $1,000,000 guarantee:** Day 1A–1F Nov 30–Dec 2; Day 2 Dec 3; final table Dec 4. Terms allow **unlimited re-entry per starting flight until level 9**; advancing to Day 2 prevents entry into a later starting flight. Published fee split: $695 prize pool + $72 tournament fee + $33 staff service charge = $800. Separate from strict single-entry.
- **$1,100 WPT Prime Championship, $5,000,000 guarantee:** Day 1A–1D Dec 5–8; later days through Dec 12. Terms allow **one entry and one re-entry per starting flight until level 10**; a Day 2 player may not enter another starting flight. Published split: $970 prize pool + $90 tournament fee + $40 staff service charge = $1,100. Separate from strict single-entry.
- **$600 NLH Turbo, $50,000 guarantee:** One-day 9 PM events are listed on Dec 5–9, 12, and 14, plus Dec 21 at 6 PM. Its event terms allow **unlimited re-entry until level 9**. Include separately if the current dataset has this schedule; it is not single-entry.
- The general Wynn terms require players to be at least 21 and members of Wynn Rewards; management reserves the ability to revise, suspend, or cancel events. Terms are event-specific.

### Caesars daily formats
Source: [Caesars official Las Vegas poker tournaments guide](https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip).

- The article describes Caesars Palace daily $100 NLH starts at 10 AM, 2 PM, 6 PM and 9 PM, each with a $1,000 guarantee, and a **$50 add-on for 15,000 chips** at the first break. Put this in the separate spend-more section; the page is recurring schedule information, not a dated calendar.
- The same page describes Horseshoe Las Vegas daily NLH starts at 9 AM, 11 AM, 2 PM, 5 PM, 8 PM and 11 PM, but does **not** state event-level buy-ins, guarantees or one-entry rules there. The recurring 9 AM start means “earliest verified start is 10:10 AM” should be phrased as applying only to the Venetian dated series—not all checked Strip sources. No 8 AM start was found in the sources checked.

### Hotel fee details / presentation issue

- [Wynn Resort Information](https://www.wynnlasvegas.com/about-us/resort-information) states a daily resort fee of **$55 plus tax**.
- [Venetian hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) state Clark County room tax is **13.38%**. This is a hotel operator's official disclosure (not an independently fetched County page); preserve that distinction if used in calculations.
- **Venetian wording to flag:** the [2026 poker-rate page](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) publishes $119/$209 “from” rates and says there is a $55 resort fee per night; the separate [resort-fee page](https://www.venetianlasvegas.com/resort/resort-fee.html) says “Rates include a daily Resort Fee of $55 plus tax.” Exact meaning for the poker offer should be confirmed at reservation. The poker rate also requires six live cash hours or a $300+ tournament buy-in per night; rates depend on availability and play requirements.
- [Venetian series overview](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html) on the snapshot date still labels the WPT Fall Festival (Oct 28–Nov 15) “Current Series” while showing DSE IV (starting Nov 16) as “Next Series.” The dates on one official page are internally inconsistent with its status label.

## Request to the integration owner (do not edit their files here)

Please update the existing source-owned tournament/re-entry and schedule data/pages with the Wynn event-specific re-entry terms and Caesars' 9 AM Horseshoe recurring schedule / Caesars Palace paid add-on fact. Also consider adding the Venetian stale series-label and resort-fee wording ambiguity to its flagged rows. Keep date-specific hotel totals and unverified entry caps blank. The main integration files are owned/maintained in the already-merged sessions recorded in `COORDINATION.md`.

## Verification performed

Fetched and read the official Wynn WPT schedule and structures PDF across the relevant chunks (including the $600, $800, WPT Prime and $600 Turbo event terms), the Wynn official room resort-information page, Caesars official tournament guide, Venetian official hotel terms and fee pages, and Venetian series overview. Only the facts above were carried forward; unknown entry rules and date-specific prices are not inferred.
