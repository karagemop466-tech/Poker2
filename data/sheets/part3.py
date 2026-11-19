# Verified readings, official Venetian DSE IV structure sheets, retrieved 2026-11-17.

from part1 import BASE, SHEETS

def s(n, **kw):
    kw["sheet"] = n
    kw["url"] = BASE + "dse_nov_2026-structure_%d.pdf" % n
    kw.setdefault("retrieved", "2026-11-17")
    SHEETS[n] = kw

s(17,
  title="$600 No Limit Hold'em Seniors (1Day) - MUST BE 50+",
  events=[24, 32],
  buy_in=600, fee=90, pool_per_entry=510,
  start="10:10 AM", chips=40000, level_min=30,
  late_reg="10 levels + Break (~3:55 PM)",
  guarantee="$40,000",
  payout_pct="15% of the field",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In.",
  eligibility="Must be 50+ years of age and have a Venetian Rewards card to participate. Any player who buys into this event that is not 50+ years of age will not be entitled to any prize money or a refund of their buy in.",
  flags=["age-restricted: 50+"],
  notes="10 numbered rules; none mentions re-entry, rebuy or add-on. Earliest verified Venetian start in the series (10:10 AM).")

s(18,
  title="$200 No Limit Hold'em RaceDay Stack (1Day)",
  eligibility="Must be 21+ years of age and have a Venetian Rewards card to participate.",
  events=[3, 4, 5],
  buy_in=200, fee=35, pool_per_entry=165,
  start="10:10 AM", chips=30000, level_min="20/15",
  late_reg="6 levels + Break (~12:25 PM)",
  guarantee=None,
  payout_pct="12.5% of the field",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$35 of the $200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $165 of every $200 Buy In.",
  flags=["no guarantee published on the sheet", "accelerating structure: 20-minute levels then 15-minute levels",
         "official subtitle on the schedule page: 'Race to finish before the Race' - a hard finish constraint"],
  notes="10 numbered rules; none mentions re-entry, rebuy or add-on.")

s(19,
  title="$100 NLH LIPS Ladies - Milestone Satellite to $800 LIPS Ladies Event #39",
  events=[33, 37],
  buy_in=100, fee=20, pool_per_entry=80,
  start="4:10 PM", chips=20000, level_min=20,
  late_reg="6 levels + Break (~6:25 PM)",
  guarantee="2 Seats",
  payout_pct="seats into Event #39; odd monies paid as one additional payout",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$20 of the $100 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $80 of every $100 Buy In.",
  eligibility="Open to Female players who must be 21+ years of age and have a Venetian Rewards card.",
  flags=["SATELLITE - prize is entry into Event #39, not cash", "Milestone rule: 200,000 chips instantly awards a seat and the player's chips are removed"],
  notes="13 numbered rules. Not a cash-prize event; excluded from like-for-like prize comparison.")

s(20,
  title="$1,100 No Limit Hold'em Seniors - MUST BE 50+ (Day A+B, Day 2 10:00 AM)",
  events=[49],
  buy_in=1100, fee=140, pool_per_entry=960,
  start="10:10 AM", chips=40000, level_min=40,
  late_reg="9 levels + Break (~4:55 PM)",
  guarantee="$300,000",
  payout_pct="each flight plays to ~15% remaining; Day 2 combines 1A+1B, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$140 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $960 of every $1,100 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  eligibility="Must be 50+ years of age and have a Venetian Rewards card to participate.",
  flags=["multi-flight", "age-restricted: 50+"],
  notes="13 numbered rules.")

s(21,
  title="$2,200 No Limit Hold'em - PokerAtlas Championship Title Event (Day 1A)",
  events=[47],
  buy_in=2200, fee=225, pool_per_entry=1975,
  start="10:10 AM", chips=40000, level_min=40,
  late_reg="9 levels + Break (~4:55 PM)",
  guarantee="$1,000,000",
  payout_pct="Day 2 plays down to 7 players; Day 3 is a PokerGO-streamed final table",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$225 of the $2,200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $1,975 of every $2,200 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (Day 1A / Day 1B)", "largest buy-in in the series"],
  notes="13 numbered rules. Footer: 'SEE OTHER STRUCTURE SHEET FOR DAY 1B'.")

s(22,
  title="$300 Pot Limit Omaha Double Board Bomb Pot (1Day)",
  eligibility="Must be 21+ years of age and have a Venetian Rewards card to participate.",
  events=[20],
  buy_in=300, fee=58, pool_per_entry=242,
  start="12:10 PM", chips=30000, level_min=30,
  late_reg="8 levels + break (~4:40 PM)",
  guarantee="$10,000",
  payout_pct="12.5% of the field; plays 8-handed",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$58 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $242 of every $300 Buy In.",
  flags=["non-NLH variant: double board bomb pot PLO", "ante-only structure, no blinds"],
  notes="13 numbered rules; none mentions re-entry, rebuy or add-on.")
