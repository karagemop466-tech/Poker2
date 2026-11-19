# Official re-verification record — arena/2c7e846d-poker2 (2026-11-19)

Scope: the nine official Venetian DeepStack Extravaganza IV structure sheets behind the 15 research
candidates on `/2026/`, the official Venetian schedule page (candidate rows), and the Clark County
room-tax source behind the 13.38% calculator rate. Every fact below was read in this session with the
page-fetch tool. Nothing here is a booking recommendation, a hotel quote, or a walking-time measurement.

## 1. Sources read on 2026-11-19

| # | Source (official host) | What was read | Retrieved |
|---|---|---|---|
| S1 | [Structure sheet 5](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf) | $300 NLH, events 2 and 12 — all 10 numbered rules | 2026-11-19 |
| S2 | [Structure sheet 6](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf) | $400 NLH, event 10 — all 10 rules | 2026-11-19 |
| S3 | [Structure sheet 7](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf) | $600 NLH, events 14, 28, 63 — all 10 rules | 2026-11-19 |
| S4 | [Structure sheet 17](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_17.pdf) | $600 NLH Seniors, events 24 and 32 — all 10 rules | 2026-11-19 |
| S5 | [Structure sheet 18](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_18.pdf) | $200 NLH RaceDay Stack, events 3, 4, 5 — all 10 rules | 2026-11-19 |
| S6 | [Structure sheet 22](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_22.pdf) | $300 PLO Double Board Bomb Pot, event 20 — all 13 rules | 2026-11-19 |
| S7 | [Structure sheet 23](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_23.pdf) | $600 PLO Double Board Bomb Pot, event 57 — all 13 rules | 2026-11-19 |
| S8 | [Structure sheet 28](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_28.pdf) | $600 Big O, event 27 — all 10 rules | 2026-11-19 |
| S9 | [Structure sheet 29](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_29.pdf) | $200 NLH, event 6 — all 10 rules | 2026-11-19 |
| S10 | [Official schedule page, DSE IV](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) | All four chunks: date, start time, event number, structure-sheet link for every row | 2026-11-19 |
| S11 | [Clark County Dept. of Business License letter, 2016-11-15](https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:7436500e-cac4-420a-b23a-02d3fec69900/original/as/room-tax-increase-transient-lodging-letter-111616.pdf) | Adopted combined rate: Primary Gaming Corridor = 13.38% (12.0 + 0.5 LVCVA + 0.88 stadium) | 2026-11-19 |
| S12 | [Venetian Rewards sign-in page](https://www.venetianlasvegas.com/venetianrewards.html) | Only a sign-in form. It does not state membership cost or enrolment terms. | 2026-11-19 |

## 2. Printed eligibility (rule 2 on each sheet)

- Sheets 5, 6, 7, 18, 22, 23, 28, 29: *"Must be 21+ years of age and have a Venetian Rewards card to participate."*
  These cover 13 open candidate events: 2, 3, 4, 5, 6, 10, 12, 14, 20, 27, 28, 57, 63.
- Sheet 17: *"Must be 50+ years of age and have a Venetian Rewards card to participate."* Covers events 24 and 32, with a
  forfeiture sentence for players who are not 50+.

The `/2026/` pages previously said "open to any player aged 21+" and did not mention the card. They now state the
printed condition. Membership cost and enrolment terms are **not verified** and are left blank (flag N-04).

## 3. Comparison of printed values with the stored dataset

Method: `printed` values from S1–S9 and S10 compared with `data/verified2026/dataset.json` by script
(`buy_in`, `fee`, `gtd`, `start`, `reg_close`, `chips`, and date/start in the schedule).

| Sheet | Events | Compared fields | Result |
|---|---|---|---|
| 5 | 2, 12 | buy-in $300, fee $58, GTD $10,000, start 11:10 AM, late reg ~4:55 PM, 40,000 chips | match (6/6 × 2) |
| 6 | 10 | buy-in $400, fee $65, GTD $15,000, start 11:10 AM, late reg ~4:55 PM, 40,000 chips | match |
| 7 | 14, 28, 63 | buy-in $600, fee $90, GTD $30K (14, 63) / $40K (28), start 11:10 AM, late reg ~4:55 PM, 40,000 chips | match |
| 17 | 24, 32 | buy-in $600, fee $90, GTD $40,000, start 10:10 AM, late reg ~3:55 PM, 40,000 chips | match |
| 18 | 3, 4, 5 | buy-in $200, fee $35, no printed GTD, start 10:10 AM, late reg ~12:25 PM, 30,000 chips | match |
| 22 | 20 | buy-in $300, fee $58, GTD $10,000, start 12:10 PM, late reg ~4:40 PM, 30,000 chips | match |
| 23 | 57 | buy-in $600, fee $90, GTD $25,000, start 12:10 PM, late reg ~4:40 PM, 30,000 chips | match |
| 28 | 27 | buy-in $600, fee $90, GTD $25,000, start 12:10 PM, late reg ~4:40 PM, 30,000 chips | match |
| 29 | 6 | buy-in $200, fee $40, no printed GTD, start 11:10 AM, late reg ~3:40 PM, 30,000 chips | match |

Mismatches: **0** of 90 field comparisons across 15 events.

Schedule rows (S10) for the 15 candidates — date and start time: **0 mismatches**. Event 2 (Nov 18) is outside
the upcoming filter, but the row was checked.

## 4. Single-entry clause check (re-read)

All nine sheets read on 2026-11-19 (S1–S9) were read rule by rule. **None** prints a re-entry, rebuy or
add-on clause, so the single-entry status is still *silent*, not *confirmed*. Silence is not a prohibition. The
Confirmed single-entry count stays 0 (flag F-01). Re-reading the sheets did not change the classification.

## 5. Tax rate

The 13.38% Primary Gaming Corridor rate is supported by S11 (adopted 2016, effective 2017). The site's
`ROOM_TAX` source is the Clark County 2021 guide already in the dataset (read 2026-11-17 by an earlier session).
The Venetian hotel terms page, cited there as corroboration, was **not** re-read in this session. S11 is a 2016 notice. A live county rate table was not reached, so the current
rate is recorded as **consistent with the official notice**, not as a 2026 county table check.

## 6. What this record does NOT establish

- Membership cost or enrolment terms for the Venetian Rewards card (S12 is a sign-in form).
- Any hotel rate, checkout total, resort fee for a stay, or cancellation terms (not re-read in this session).
- Walking time from any hotel to the Venetian poker room. No map-service measurement was taken.
- Whether any event is single-entry. No candidate was promoted.
- Structure sheets other than the nine listed. Those stay on their 2026-11-17 transcription date.
