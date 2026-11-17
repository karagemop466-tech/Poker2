# Verified readings, official Venetian DSE IV structure sheets, retrieved 2026-11-17.

from part1 import BASE, SHEETS

def s(n, **kw):
    kw["sheet"] = n
    kw["url"] = BASE + "dse_nov_2026-structure_%d.pdf" % n
    kw.setdefault("retrieved", "2026-11-17")
    SHEETS[n] = kw

s(29,
  title="$200 No Limit Hold'em (1Day)",
  events=[6],
  buy_in=200, fee=40, pool_per_entry=160,
  start="11:10 AM", chips=30000, level_min=30,
  late_reg="8 levels + Break (~3:40 PM)",
  guarantee=None,
  payout_pct="12.5% of the field",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $160 of every $200 Buy In.",
  flags=["no guarantee printed on the sheet"],
  notes="10 numbered rules; none mentions re-entry, rebuy or add-on.")

s(30,
  title="$200 No Limit Hold'em Progressive Knock-Out Bounty (PKO) (1Day)",
  events=[8],
  buy_in=200, fee=40, pool_per_entry=160,
  start="5:10 PM", chips=25000, level_min=30,
  late_reg="8 levels + Break (9:40 PM)",
  guarantee="$8,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field",
  bounty="PKO: each player starts as a $50 bounty; eliminator keeps half and adds half to own bounty",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $160 of every $200 Buy In.",
  flags=["bounty event (PKO) - guarantee includes bounty money"],
  notes="12 numbered rules; none mentions re-entry, rebuy or add-on.")

s(31,
  title="$600 No Limit Hold'em - LIPS Poker Jingle Tag Team Event",
  events=[35],
  buy_in=600, fee=80, pool_per_entry=510,
  start="10:10 AM", chips=40000, level_min=30,
  late_reg="8 levels + Break (~2:40 PM)",
  guarantee="$10,000",
  payout_pct="12.5% of the field",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$80 of the $600 Buy-In is withheld for house fees (Rake + Staff). $10 of the $600 Buy In will be withheld as a flat fee for Vegas Connected, INC, DBA Ladies International Poker Series (LIPS). Prize pool consists of $510 of every $600 Buy In.",
  flags=["TAG TEAM event - two players per entry, rotating every level",
         "Teams: Female/Female OR Female/Male", "buy-in is per team on the sheet's own wording"],
  notes="11 numbered rules. Rule 8: 'Teams will rotate their players at the start of every level. Each team member must play every other level until the event concludes.' Not a solo single-entry event.")

s(32,
  title="$800 NLH LIPS Ladies (2Day) - Women in Poker Main Event",
  events=[39],
  buy_in=800, fee=90, pool_per_entry=690,
  start="Day 1 Dec 10 @ 10:10 AM; Day 2 Dec 11 @ 10:00 AM", chips=40000, level_min=40,
  late_reg="9 levels + Break (~4:55 PM)",
  guarantee="$40,000",
  payout_pct="Day 1 to ~12.5%; Day 2 to 7 players for a PokerGO-streamed final table (~7:00 PM)",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$90 of the $800 Buy-In is withheld for house fees (Rake + Staff). $20 of the $800 Buy In will be withheld as a flat fee for Vegas Connected, INC, DBA Ladies International Poker Series (LIPS). Prize pool consists of $690 of every $800 Buy In.",
  eligibility="Must be a female 21+ years of age and have a Venetian Rewards card to participate.",
  flags=["restricted field: female players only", "single Day 1 with a Day 2 - not multi-flight"],
  notes="12 numbered rules; none mentions re-entry, rebuy or add-on.")

s(33,
  title="$600 No Limit Hold'em LIPS - Kings and Queens Bounty (open to all players)",
  events=[43],
  buy_in=600, fee=80, pool_per_entry=510,
  start="11:10 AM", chips=40000, level_min=30,
  late_reg="10 levels + Break (4:55 PM)",
  guarantee="$30,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field",
  bounty="$200 bounty per elimination; winner keeps own bounty. Trophy to last King and last Queen standing",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$80 of the $600 Buy-In is withheld for house fees (Rake + Staff). $10 of the $600 Buy In will be withheld as a flat fee for Vegas Connected, INC, DBA Ladies International Poker Series (LIPS). Prize pool consists of $510 of every $600 Buy In.",
  flags=["bounty event - guarantee includes bounties", "a $10 LIPS fee is on top of the $80 house fee"],
  notes="11 numbered rules; none mentions re-entry, rebuy or add-on.")

s(34,
  title="$1,100 No Limit Hold'em Progressive Knock-Out Bounty (PKO) (1Day)",
  events=[52],
  buy_in=1100, fee=130, pool_per_entry=970,
  start="11:10 AM", chips=40000, level_min=30,
  late_reg="10 levels + Break (4:55 PM)",
  guarantee="$75,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field",
  bounty="PKO: each player starts as a $200 bounty; eliminator keeps half and adds half to own bounty",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$130 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $970 of every $1,100 Buy In.",
  flags=["bounty event (PKO) - guarantee includes bounty money"],
  notes="12 numbered rules; none mentions re-entry, rebuy or add-on.")
