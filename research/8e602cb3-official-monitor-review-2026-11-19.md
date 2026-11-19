# `/2026/` pending monitor-change review — 2026-11-19 (arena/8e602cb3-poker2)

This review addresses only the four URLs marked `review_required` by the latest committed
`data/verified2026/checks.json` run (`2026-11-18T15:29:01Z`). I re-read each official source through
the page-fetch tool on 2026-11-19. The listed hash is the last automated baseline from that run; it
is **not** a hash computed from today's page-fetch response. A review acknowledgement for that exact
baseline does not mean the monitor ran again today. The next scheduled fetch must reopen a warning if
it observes another content hash.

## Sources and comparison

| URL | Last recorded automated hash / change | What the official source says on 2026-11-19 | Comparison / disposition |
|---|---|---|---|
| [Wynn Resort Policies & Information](https://www.wynnlasvegas.com/about-us/resort-information) | `f72a33f1d4b7e22f` / `CHANGED` | Check-in 3 p.m.; check-out 12 p.m.; daily resort fee `$55 plus tax`; complimentary self-parking for up to two vehicles is listed among the fee inclusions. | The resort-fee and parking facts match the published Wynn/Encore hotel rows. Wynn and Encore `resort_fee_checked` still said `2026-11-16` in the pre-integration data, so the date should advance to `2026-11-19`; no room price or tax rate is published on this page. |
| [Venetian Poker Room](https://www.venetianlasvegas.com/resort/casino/poker.html) | `8c8ae728c8d7c0a0` / `CHANGED` | Poker room at The Palazzo, level 2, Grand Canal Shoppes; open 24 hours; 50 tables; non-registered guests who play at least three hours in tournaments or cash games receive complimentary self-parking. | Matches the room location, hours/table count, and parking statements already published. The hotel data's parking note mentions the current three-hour policy, but does not store a `parking_checked` field; add the retrieval date during final integration. No walking time is published by the resort. |
| [Venetian DeepStack series overview](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html) | `9513be7c43ca178c` / `CHANGED` | Current series: DSE IV, Nov 16–Dec 23, 2026, more than `$3.6M` in guarantees. Next: DSE NYE, Dec 24, 2026–Jan 10, 2027, more than `$1.1M`. Next: DeepStack Showdown, Jan 11–Feb 14, 2027, more than `$2.2M`. | The source change is genuine: the page now identifies DSE IV as the current series rather than the prior WPT Fall Festival. The current series window and the following series windows agree with the linked official pages already listed in the dashboard. This overview is not a substitute for the dated schedules or structure sheets; no event row or entry rule was changed from it. |
| [Venetian DSE IV structure sheet 30](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_30.pdf) | `a769510ec44c9086` / `CHANGED` | `$200 No Limit Hold'em (1Day)`, PKO; Event 08; 5:10 p.m.; 25,000 starting chips; 30-minute levels; late registration through eight levels plus break (9:40 p.m.); `$8,000` guarantee inclusive of prize pool plus total bounties; `$40` house fees / `$160` prize pool; pays 12.5% of field. | Matches the event 8 transcription. The sheet does not state a whole-event maximum-entry limit, no-re-entry, no-rebuy or no-add-on policy. It remains unconfirmed and separately classified as a bounty/PKO event; this review does not promote it to single-entry. A parallel 2026-11-19 audit also re-read Sheet 30; its record is in [PR #96](https://github.com/karagemop466-tech/Poker2/pull/96). |

## What this review does not establish

- It does not update the last automated fetch timestamp or establish a new monitor baseline.
- It does not prove that the source remains unchanged after 2026-11-19.
- It does not confirm any strict single-entry / freezeout event; the confirmed count remains zero.
- It does not create a room quote, hotel booking, walking-time measurement, or tournament finish time.

The exact-hash acknowledgements are intended for `data/verified2026/reviewed-hashes.json`. They will
suppress only the reviewed versions; a later hash mismatch remains flagged by `scripts/recheck2026.py`.
