# Verified readings of official Venetian DeepStack Extravaganza IV structure sheets.
# Retrieved 2026-11-17 from https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/
# Each entry records what the official PDF prints. "silent" means the sheet contains no
# re-entry / rebuy / add-on clause at all - which is NOT the same as a prohibition.
# Only clauses actually printed on the sheet are quoted.

BASE = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/"

SHEETS = {}

def s(n, **kw):
    kw["sheet"] = n
    kw["url"] = BASE + "dse_nov_2026-structure_%d.pdf" % n
    kw.setdefault("retrieved", "2026-11-17")
    SHEETS[n] = kw

s(1,
  title="$200 No Limit Hold'em Bounty (1Day)",
  events=[9, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64],
  buy_in=200, fee=40, pool_per_entry=160,
  start="5:10 PM", chips=25000, level_min=30,
  late_reg="8 levels + Break (9:40 PM)",
  guarantee="$8,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field",
  bounty="$50 bounty per elimination, split equally on identical hands",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $160 of every $200 Buy In.",
  flags=["bounty event - guarantee includes bounties"],
  notes="12 numbered rules; none mentions re-entry, rebuy or add-on.")

s(2,
  title="$400 No Limit Hold'em (multi-flight 1A+1B, Day 2 11:00 AM)",
  events=[7],
  buy_in=400, fee=70, pool_per_entry=330,
  start="11:10 AM", chips=40000, level_min=40,
  late_reg="9 levels + Break (5:55 PM)",
  guarantee="$75,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$70 of the $400 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $330 of every $400 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight: entering more than one flight is not expressly prohibited; only bagging into Day 2 blocks a later flight"],
  notes="13 numbered rules.")

s(3,
  title="$400 No Limit Hold'em (multi-flight 1A+1B+1C, Day 2 11:00 AM)",
  events=[19],
  buy_in=400, fee=70, pool_per_entry=330,
  start="11:10 AM", chips=40000, level_min=40,
  late_reg="9 levels + Break (5:55 PM)",
  guarantee="$75,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$70 of the $400 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $330 of every $400 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight"],
  notes="13 numbered rules.")

s(4,
  title="$600 No Limit Hold'em (multi-flight 1A+1B+1C, Day 2 11:00 AM)",
  events=[59],
  buy_in=600, fee=95, pool_per_entry=505,
  start="11:10 AM", chips=40000, level_min=40,
  late_reg="9 levels + Break (5:55 PM)",
  guarantee="$150,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$95 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $505 of every $600 Buy In. On Day 1A only, players who register before the start of the event (11:10 a.m.), will receive a $20 discount on house fees for a total buy in of $580 instead of $600.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight", "early-registration discount changes the total cost, not the number of entries"],
  notes="13 numbered rules.")

s(5,
  title="$300 No Limit Hold'em (1Day)",
  eligibility="Must be 21+ years of age and have a Venetian Rewards card to participate.",
  events=[2, 12],
  buy_in=300, fee=58, pool_per_entry=242,
  start="11:10 AM", chips=40000, level_min=30,
  late_reg="10 levels + Break (~4:55 PM)",
  guarantee="$10,000",
  payout_pct="12.5% of the field",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$58 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $242 of every $300 Buy In.",
  flags=[],
  notes="10 numbered rules; none mentions re-entry, rebuy or add-on. One-day freezeout structure.")

s(6,
  title="$400 No Limit Hold'em (1Day)",
  eligibility="Must be 21+ years of age and have a Venetian Rewards card to participate.",
  events=[10],
  buy_in=400, fee=65, pool_per_entry=335,
  start="11:10 AM", chips=40000, level_min=30,
  late_reg="10 levels + Break (~4:55 PM)",
  guarantee="$15,000",
  payout_pct="12.5% of the field",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$65 of the $400 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $335 of every $400 Buy In.",
  flags=[],
  notes="10 numbered rules; none mentions re-entry, rebuy or add-on.")

s(7,
  title="$600 No Limit Hold'em (1Day)",
  eligibility="Must be 21+ years of age and have a Venetian Rewards card to participate.",
  events=[14, 28, 63],
  buy_in=600, fee=90, pool_per_entry=510,
  start="11:10 AM", chips=40000, level_min=30,
  late_reg="10 levels + Break (~4:55 PM)",
  guarantee="$30,000 for Event #14 and #63; $40,000 for Event #28",
  payout_pct="12.5% of the field",
  bounty=None,
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In.",
  flags=["guarantee differs by event number on the same sheet"],
  notes="10 numbered rules; none mentions re-entry, rebuy or add-on.")

s(8,
  title="$200 No Limit Hold'em Valuetown Bounty (1Day) - PokerAtlas PRO $20 rake discount",
  events=[18, 58],
  buy_in=200, fee=40, pool_per_entry=160,
  start="5:10 PM", chips=25000, level_min=30,
  late_reg="8 levels + Break (9:40 PM)",
  guarantee="$20,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field",
  bounty="$50 bounty per elimination",
  multi_flight=False,
  reentry="IMPLIED - see quote", addon="silent", rebuy="silent",
  fee_quote="PokerAtlas PRO players will receive a twenty ($20) rake discount on their initial $200 buy in only, for a total buy in of $180 instead of $200. ... All subsequent buy in's after the initial buy in will be $200.",
  flags=["RE-ENTRY INDICATED: the sheet prices 'subsequent buy in's' at $200, so more than one buy-in per player is contemplated",
         "bounty event - guarantee includes bounties",
         "paid PokerAtlas PRO membership buys a $20 discount - a spend-to-advantage element"],
  notes="13 numbered rules. The only sheet in 1-10 that prices a second buy-in.")

s(9,
  title="$300 No Limit Hold'em - Day B+D @ 5:10 PM (Day 2 12:00 PM)",
  events=[1],
  buy_in=300, fee=60, pool_per_entry=240,
  start="5:10 PM", chips=30000, level_min=30,
  late_reg="6 levels + Break (~8:40 PM)",
  guarantee="$75,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines 1A-1D, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$60 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $240 of every $300 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (1A/1B/1C/1D)", "sheet covers the PM flights only"],
  notes="13 numbered rules. Footer: 'SEE OTHER STRUCTURE SHEET FOR DAYS A+C'.")

s(10,
  title="$300 No Limit Hold'em - Day A+C @ 11:10 AM (Day 2 12:00 PM)",
  events=[1],
  buy_in=300, fee=60, pool_per_entry=240,
  start="11:10 AM", chips=30000, level_min=40,
  late_reg="6 levels + Break (~3:40 PM)",
  guarantee="$75,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines 1A-1D, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$60 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $240 of every $300 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (1A/1B/1C/1D)", "sheet covers the AM flights only"],
  notes="13 numbered rules. Footer: 'SEE OTHER STRUCTURE SHEET FOR DAYS B+D'.")
