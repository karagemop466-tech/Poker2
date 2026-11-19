# Verified readings, official Venetian DSE IV structure sheets, retrieved 2026-11-17.

from part1 import BASE, SHEETS

def s(n, **kw):
    kw["sheet"] = n
    kw["url"] = BASE + "dse_nov_2026-structure_%d.pdf" % n
    kw.setdefault("retrieved", "2026-11-17")
    SHEETS[n] = kw

s(23,
  title="$600 Pot Limit Omaha Double Board Bomb Pot (1Day)",
  eligibility="Must be 21+ years of age and have a Venetian Rewards card to participate.",
  events=[57],
  buy_in=600, fee=90, pool_per_entry=510,
  start="12:10 PM", chips=30000, level_min=30,
  late_reg="8 levels + break (~4:40 PM)",
  guarantee="$25,000",
  payout_pct="12.5% of the field; plays 8-handed",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In.",
  flags=["non-NLH variant: double board bomb pot PLO"],
  notes="13 numbered rules; none mentions re-entry, rebuy or add-on.")

s(24,
  title="$260 No Limit Hold'em - Milestone Satellite to $2,200 Event #47",
  events=[41, 44],
  buy_in=260, fee=40, pool_per_entry=220,
  start="4:10 PM", chips=20000, level_min=20,
  late_reg="6 levels + Break (~6:25 PM)",
  guarantee="2 Seats",
  payout_pct="seats into Event #47; odd monies as one additional payout",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$40 of the $260 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $220 of every $260 Buy In.",
  flags=["SATELLITE - prize is entry into Event #47, not cash", "Milestone rule: 200,000 chips instantly awards a seat"],
  notes="13 numbered rules.")

s(25,
  title="$260 No Limit Hold'em Turbo - Milestone Satellite to $2,200 Event #47",
  events=[45, 46, 48],
  buy_in=260, fee=35, pool_per_entry=225,
  start="Event #45 8:10 PM; Event #46 9:10 AM; Event #48 12:10 PM",
  chips=20000, level_min=15,
  late_reg="6 levels",
  guarantee="2 Seats",
  payout_pct="seats into Event #47; odd monies as one additional payout",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$35 of the $260 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $225 of every $260 Buy In.",
  flags=["SATELLITE - prize is entry into Event #47, not cash", "start time differs per event number on the same sheet",
         "Event #46 at 9:10 AM is the earliest verified start in the series"],
  notes="13 numbered rules.")

s(26,
  title="$400 Pot Limit Omaha Bounty (1Day)",
  events=[17],
  buy_in=400, fee=60, pool_per_entry=340,
  start="12:10 PM", chips=30000, level_min=30,
  late_reg="8 levels + break (~4:40 PM)",
  guarantee="$15,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field; plays 8-handed",
  bounty="$100 bounty per elimination; winner keeps own bounty",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$60 of the $400 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $340 of every $400 Buy In.",
  flags=["bounty event - guarantee includes bounties", "non-NLH variant"],
  notes="12 numbered rules; none mentions re-entry, rebuy or add-on. Structure uses a 'Call or Make It' column.")

s(27,
  title="$600 Pot Limit Omaha Bounty (1Day)",
  events=[40],
  buy_in=600, fee=90, pool_per_entry=510,
  start="12:10 PM", chips=30000, level_min=30,
  late_reg="8 levels + break (~4:40 PM)",
  guarantee="$25,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field; plays 8-handed",
  bounty="$200 bounty per elimination; winner keeps own bounty",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In.",
  flags=["bounty event - guarantee includes bounties", "non-NLH variant"],
  notes="12 numbered rules; none mentions re-entry, rebuy or add-on.")

s(28,
  title="$600 BIG O (1Day)",
  eligibility="Must be 21+ years of age and have a Venetian Rewards card to participate.",
  events=[27],
  buy_in=600, fee=90, pool_per_entry=510,
  start="12:10 PM", chips=30000, level_min=30,
  late_reg="8 levels + break (~4:40 PM)",
  guarantee="$25,000",
  payout_pct="12.5% of the field; plays 8-handed",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). Prize pool consists of $510 of every $600 Buy In.",
  flags=["non-NLH variant: Big O"],
  notes="10 numbered rules; none mentions re-entry, rebuy or add-on.")
