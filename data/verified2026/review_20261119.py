"""Fresh official reads by arena/a29d9f35-poker2, 2026-11-19 UTC.
These are not a claim that every previously transcribed document was re-read today.
"""
CHECKED = '2026-11-19'
WYNN_PAGE = 'https://www.wynnlasvegas.com/casino/poker'
WYNN_RULES = 'https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf'
SCHEDULE = 'https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html'
FEE = 'https://www.venetianlasvegas.com/resort/resort-fee.html'

def field(value, excerpt):
    return dict(value=value, excerpt=excerpt, source=WYNN_RULES, retrieved=CHECKED)

WYNN_DAILY = [
    dict(name='Monday–Thursday NLH', days='Monday–Thursday', start='12 p.m.', entry=200,
         guarantee=10000, house_fee=26, staff_fee=12, pool=162, chips=25000, level_minutes=30,
         late_registration='Start of level 9 (approximately 4:30 p.m.)', finish=None,
         single_entry=field(False, 'The Tournament entry fee, as well as the re-entry fee, is $200'),
         reentry=field(200, 'Registration and re-entries will be available until the start of level 9'),
         rebuy=field(None, ''), addon=field(None, ''),
         fee=field(200, '$26 for the Tournament fee, $12 for the poker staff service charge, and $162 for the Tournament prize pool.')),
    dict(name='Friday NLH Rebuy & Add-on', days='Friday', start='12 p.m.', entry=240,
         guarantee=40000, house_fee=35, staff_fee=15, pool=190, chips=25000, level_minutes=30,
         late_registration='Start of level 9 (approximately 4:30 p.m.)', finish=None,
         single_entry=field(False, 'Unlimited $200 rebuys for 25,000 tournament chips'),
         reentry=field(False, 'Re-entry is NOT allowed. All rebuys must be done immediately from the player’s original seat.'),
         rebuy=field(200, 'Unlimited $200 rebuys for 25,000 tournament chips are available any time a player is at 15,000 chips or less.'),
         addon=field(100, 'One (1) $100 addon for 15,000 tournament chips is available any time until the end of registration.'),
         fee=field(240, 'The Tournament entry fee is $240 ... $35 ... Tournament fee and $15 ... service charge for poker staff.')),
    dict(name='Saturday & Sunday NLH', days='Saturday & Sunday', start='12 p.m.', entry=200,
         guarantee=25000, house_fee=26, staff_fee=12, pool=162, chips=25000, level_minutes=30,
         late_registration='Start of level 11 (approximately 5:30 p.m.)', finish=None,
         single_entry=field(False, 'Registration, re-entries, and one (1) add-on per entry will be available'),
         reentry=field(200, 'The Tournament entry fee, as well as the re-entry fee, is $200'),
         rebuy=field(None, ''),
         addon=field(100, 'One (1) $100 add-on for 25,000 tournament chips is available any time until the end of registration.'),
         fee=field(200, '$26 for the Tournament fee, $12 for the poker staff service charge, and $162 for the Tournament prize pool.')),
    dict(name='Nightly NLH', days='Monday–Sunday', start='6 p.m.', entry=160,
         guarantee=10000, house_fee=20, staff_fee=10, pool=130, chips=25000, level_minutes=20,
         late_registration='Start of level 9 (approximately 9:00 p.m.)', finish=None,
         single_entry=field(False, 'Registration, re-entries, and one (1) add-on per entry will be available'),
         reentry=field(160, 'The Tournament entry fee, as well as the re-entry fee, is $160'),
         rebuy=field(None, ''),
         addon=field(100, 'One (1) $100 add-on for 25,000 tournament chips is available any time until the end of registration.'),
         fee=field(160, '$20 for the Tournament fee, $10 for the poker staff service charge, and $130 for the Tournament prize pool.')),
]
for row in WYNN_DAILY:
    row.update(source=WYNN_RULES, last_checked=CHECKED, category='extra-spend — excluded',
               dated_occurrence=None, suspension='May be suspended during Seniors Events, Classic Events, or other Tournament Series.')

FLAGS = [
    dict(id='N-01', area='Wynn daily rules', title='No re-entry does not mean no extra spending',
         detail='The Friday sheet prohibits re-entry but permits unlimited $200 rebuys and a $100 add-on. All four daily formats fail the strict policy; none is placed in the freezeout ranking.',
         impact='Keep in the extra-spend section. Daily availability during a series remains unverified.', source=WYNN_RULES),
    dict(id='N-02', area='Wynn Friday accounting', title='Rebuy pool split conflicts within the official sheet',
         detail='Rule 3 says $190 of each entry and rebuy funds the prize pool, but also withholds $10 staff plus $5 tournament fee from a $200 rebuy. Those rebuy figures do not reconcile. Rebuy pool contribution is not published as a settled value here.',
         impact='Ask the room for corrected written rebuy accounting; initial entry split does reconcile.', source=WYNN_RULES),
    dict(id='N-03', area='Trip readiness', title='Exact-stay hotel comparison is not possible yet',
         detail='The Dec 1–4 research screen provides comparable stay criteria, not booking preferences. No valid checkout total or cancellation deadline was captured. Google route estimates are dated, but do not time the indoor portion. Do not substitute a booking widget’s default dates or a promotional rate for a trip quote.',
         impact='No hotel winner or bookable single-entry itinerary is claimed. Keep totals blank and retain official booking links.', source=FEE),
]
