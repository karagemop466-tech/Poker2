# Verified readings, official Venetian DSE IV structure sheets, retrieved 2026-11-17.
# See part1.py for the field conventions and the base URL.

from part1 import BASE, SHEETS

def s(n, **kw):
    kw["sheet"] = n
    kw["url"] = BASE + "dse_nov_2026-structure_%d.pdf" % n
    kw.setdefault("retrieved", "2026-11-17")
    SHEETS[n] = kw

s(11,
  title="$600 No Limit Hold'em Bounty (1Day)",
  events=[16, 30, 54],
  buy_in=600, fee=90, pool_per_entry=510,
  start="11:10 AM", chips=40000, level_min=30,
  late_reg="10 levels + Break (4:55 PM)",
  guarantee="$30,000 (#16), $40,000 (#30), $50,000 (#54) - prize pool + total bounties",
  payout_pct="12.5% of the field",
  bounty="$200 bounty per elimination before the money; $500 per elimination once in the money; winner keeps own bounty",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In.",
  flags=["bounty event - guarantee includes bounties", "guarantee varies by event number"],
  notes="11 numbered rules; none mentions re-entry, rebuy or add-on.")

s(12,
  title="$800 No Limit Hold'em - Day A+C+E @ 11:10 AM (Day 2 12:00 PM)",
  events=[26],
  buy_in=800, fee=110, pool_per_entry=690,
  start="11:10 AM", chips=40000, level_min=40,
  late_reg="6 levels + Break (~3:40 PM)",
  guarantee="$500,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines 1A-1F, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $690 of every $800 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (1A-1F)", "largest guarantee in the series"],
  notes="13 numbered rules. Footer: 'SEE OTHER STRUCTURE SHEET FOR DAYS B+D+F'.")

s(13,
  title="$800 No Limit Hold'em - Day B+D @ 5:10 PM (Day 2 12:00 PM)",
  events=[26],
  buy_in=800, fee=110, pool_per_entry=690,
  start="5:10 PM", chips=40000, level_min=30,
  late_reg="6 levels + Break (~8:40 PM)",
  guarantee="$500,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines 1A-1F, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $690 of every $800 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (1A-1F)"],
  notes="13 numbered rules. Footer: 'SEE OTHER STRUCTURE SHEET FOR DAYS A+C+F'.")

s(14,
  title="$800 No Limit Hold'em - Day F (Turbo) @ 5:10 PM (Day 2 12:00 PM)",
  events=[26],
  buy_in=800, fee=110, pool_per_entry=690,
  start="5:10 PM", chips=40000, level_min=20,
  late_reg="6 levels + Break (~7:25 PM)",
  guarantee="$500,000",
  payout_pct="each flight plays to ~12.5% remaining; Day 2 combines 1A-1F, all in the money",
  bounty=None,
  multi_flight=True,
  reentry="silent on re-entry between flights", addon="silent", rebuy="silent",
  fee_quote="$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $690 of every $800 Buy In.",
  flight_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
  flags=["multi-flight (1A-1F)", "turbo flight: 20-minute levels"],
  notes="13 numbered rules.")

s(15,
  title="$300 No Limit Hold'em Bounty (1Day)",
  events=[29, 31, 34, 38, 42, 50, 51, 53, 55],
  buy_in=300, fee=50, pool_per_entry=250,
  start="5:10 PM", chips=25000, level_min=30,
  late_reg="8 levels + Break (9:40 PM)",
  guarantee="$15,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field",
  bounty="$100 bounty per elimination",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$50 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $250 of every $300 Buy In.",
  flags=["bounty event - guarantee includes bounties"],
  notes="12 numbered rules; none mentions re-entry, rebuy or add-on.")

s(16,
  title="$800 No Limit Hold'em Bounty (1Day)",
  events=[36],
  buy_in=800, fee=100, pool_per_entry=700,
  start="11:10 AM", chips=40000, level_min=30,
  late_reg="10 levels + Break (4:55 PM)",
  guarantee="$75,000 (prize pool + total bounties)",
  payout_pct="12.5% of the field",
  bounty="$200 bounty per elimination before the money; $500 once in the money; winner keeps own bounty",
  multi_flight=False,
  reentry="silent", addon="silent", rebuy="silent",
  fee_quote="$100 of the $800 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $700 of every $800 Buy In.",
  flags=["bounty event - guarantee includes bounties"],
  notes="11 numbered rules; none mentions re-entry, rebuy or add-on.")
