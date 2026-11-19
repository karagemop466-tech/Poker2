# Live official-source verification — 2026-11-19

Session: arena/755cb7af-poker2 (branch `arena/755cb7af-poker2`, from `main` `cf17894`).
Method: every document below was re-read live via the agent page-fetch tool today (bash egress to
casino/county hosts is TLS-blocked in this sandbox; `gh workflow run` returns HTTP 403, so no CI was
dispatched). Values already in the dataset were confirmed or contradicted against the live text;
nothing was inferred. Where two official documents disagree, both are cited and the conflict is
flagged — no value was silently rewritten.

## 1. Caesars Palace daily NLH flyer (PDF) — confirms PR #100 reconciliation

Official flyer (read live 2026-11-19):
https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf

| Time | Buy-In | Add-On Optional | Starting Chips | Level Times | Guarantee |
|------|--------|-----------------|----------------|-------------|-----------|
| 10 AM | $100 | $50 | 20,000 | 20 Minutes | $1,000 |
| 2 PM | $160 | $50 | 20,000 | 20 Minutes | $1,000 |
| 6 PM | $100 | $50 | 20,000 | 20 Minutes | $1,000 |
| 9 PM | $160 | $50 | 20,000 | 20 Minutes | $1,000 |

Flyer terms (verbatim from the fetched text):
- "All Tournaments feature a $50 add-on for 15,000 tournament chips that can only be taken at the first break. Registration will close at the start of level seven."
- "Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play."
- "Of the $100 buy in, $70 goes to the prize pool and $30 is held by Caesars Palace as a maintenance fee."
- "Of the $160 buy in, $115 goes to the prize pool and $45 is held by Caesars Palace as a maintenance fee."
- "Of the $50 add-on, $45 goes to the prize pool and $5 is held by Caesars Palace as a maintenance fee."
- "Must have at least 6 players to start a tournament." / "Players must be 21 years of age and over."

Result: the per-time buy-ins ($100/$160/$100/$160), fee splits ($30/$45), pool splits ($70/$115),
$50 add-on split ($45/$5), re-entry within the first break, and level-seven registration close in
`data/master.json` (rows CZP-1000AM/200PM/600PM/900PM, `last_checked` 2026-11-19) match the live
flyer exactly. The generator `scripts/build_master.py` still hardcoded $100 for all four with
`fee=None`; this session ports the flyer values into the generator so the committed output
reproduces (see W2). No new value was invented.

## 2. Caesars poker guide page — conflict with the flyer still stands

Official guide (read live 2026-11-19, chunk 1):
https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip

- "You will find four No-Limit Hold'em tournaments each day at 10 a.m., 2 p.m., 6 p.m. and 9 p.m. Every event carries a $100 buy-in, starts you with 20,000 chips, and features a $1,000 guaranteed prize pool. Blinds increase every 20 minutes ... and a $50 add-on at the first break gives you an extra 15,000 chips"

Result: the guide's "$100 for all four" claim conflicts with the flyer's $160 at 2 PM and 9 PM.
Rows keep the flyer's per-time values (the more specific document) and flag VR-028 stays open,
unchanged. Horseshoe six daily times (9, 11, 2, 5, 8, 11 PM) with "a mixture of buy-ins, levels and
guarantees" also re-confirmed; no buy-in/guarantee published there, so Horseshoe rows stay blank.

## 3. Venetian DeepStack Extravaganza IV schedule — no change observed

Official page (read live 2026-11-19, all 4 chunks):
https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html

- Series window: November 16 – December 23, 2026 ("More than $3.6 Million in guaranteed tournament prize pools").
- Spot-read all 94 printed rows across the 4 chunks (dates, times, event numbers, structure-sheet
  URLs). First rows (Event 1 flights 1A–1D, Event 2, Events 3–5 RaceDay Stack) and last rows
  (Events 59–64, Dec 20–23) match the stored dataset; no new event, removal, or retiming was
  observed in this pass. The full 94-row transcription comparison was already done by the preceding
  session (`research/live-schedule-venetian-2026-11-19.tsv`); this pass does not re-transcribe
  every row and does not advance any `last_checked` beyond what that comparison supports.
- Structure-sheet URLs on shared rows match the stored `struct_url` values (e.g. Event 2 → sheet 5,
  Events 3–5 → sheet 18, Event 14/28/63 → sheet 7).

## 4. Wynn poker page — matches stored data

Official page (read live 2026-11-19):
https://www.wynnlasvegas.com/casino/poker

- WPT World Championship: November 27 – December 21, 2026; Super Gold Million $400 buy-in /
  $3,000,000 guarantee. Matches stored data.
- Wynn Signature Series: January 11–24, 2027. Matches stored data.
- Daily tournaments: $200,000 weekly GTD; Friday $40,000 guaranteed NLH Rebuy; $10,000 guaranteed
  every evening at 6 PM. Suspension clause: "the Daily Tournament schedule will be suspended during
  each Wynn Signature, Wynn Millions, and Classic tournament series." The page does NOT name the WPT
  series, so a WPT-window suspension is NOT supported by this page (pre-existing flagged position,
  unchanged).

## 5. Venetian resort fee — unchanged

Official page (read live 2026-11-19):
https://www.venetianlasvegas.com/resort/resort-fee.html

- "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in." Matches the
  stored value ($55 + tax/night, Venetian & Palazzo). This is a mandatory-fee input, not a room
  quote or a checkout total (F-05 stays open).

## Result

No published value contradicted by today's reads except the already-flagged Caesars flyer–guide
conflict, which stays flagged (VR-028) with rows on the flyer's per-time values. Zero confirmed
single-entry events (no sheet states a one-entry rule). No dated room quote, no finish times, no
measured walking times — all remain flagged, not guessed. The only code change this session makes
is porting the verified Caesars flyer values into `scripts/build_master.py` so `data/master.json`
and the root pages reproduce byte-for-byte (fixing the `Verify site` drift failure on `main`).
