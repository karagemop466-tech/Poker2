# Verified readings, official Venetian DSE IV structure sheets, retrieved 2026-11-17.

from part1 import BASE, SHEETS

def s(n, **kw):
    kw["sheet"] = n
    kw["url"] = BASE + "dse_nov_2026-structure_%d.pdf" % n
    kw.setdefault("retrieved", "2026-11-17")
    SHEETS[n] = kw

s(35,
  title="$1,100 No Limit Hold'em - Day A+C+E @ 10:10 AM (Day 2 11:00 AM)",
  events=[56],
  buy_in=1100, fee=140, pool_per_entry=960,
  start="10:10 AM", chips=40000, level_min=40,
  late_reg="9 levels + Break (~4:55 PM)",
  guarantee="$500,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines 1A-1E, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$140 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $960 of every $1,100 Buy In. On Day 1A, players who register before the start of the event (10:10 a.m.) will receive a forty ($40) discount on house fees for a total buy in of $1,060 instead of $1,100.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (1A-1E)", "early-registration discount changes cost, not the number of entries"],
  notes="13 numbered rules. Footer: 'SEE OTHER STRUCTURE SHEET FOR DAYS B+D'.")

s(36,
  title="$1,100 No Limit Hold'em - Day B+D @ 6:10 PM (Day 2 11:00 AM)",
  events=[56],
  buy_in=1100, fee=140, pool_per_entry=960,
  start="6:10 PM", chips=40000, level_min=30,
  late_reg="9 levels + Break (~11:10 PM)",
  guarantee="$500,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines 1A-1E, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$140 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $960 of every $1,100 Buy In. On Day 1B, players who register before the start of the event (6:10 PM.) will receive a forty ($40) discount on house fees for a total buy in of $1,060 instead of $1,100.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (1A-1E)", "late registration runs to ~11:10 PM on this flight"],
  notes="13 numbered rules. Footer: 'SEE OTHER STRUCTURE SHEET FOR DAYS A+C+E'.")

s(37,
  title="$2,200 No Limit Hold'em - PokerAtlas Championship Title Event (Day 1B @ 6:10 PM)",
  events=[47],
  buy_in=2200, fee=225, pool_per_entry=1975,
  start="6:10 PM", chips=40000, level_min=30,
  late_reg="9 levels + Break (~11:10 PM)",
  guarantee="$1,000,000",
  payout_pct="Day 2 plays down to 7 players; Day 3 is a PokerGO-streamed final table at 11:00 AM",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$225 of the $2,200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $1,975 of every $2,200 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (Day 1A / Day 1B)", "largest buy-in in the series"],
  notes="13 numbered rules. Footer: 'SEE OTHER STRUCTURE SHEET FOR DAY 1A'.")
