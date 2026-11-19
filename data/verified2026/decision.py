"""New official reads and explicitly hypothetical comparison inputs (2026-11-19)."""
READ = '2026-11-19'
VENETIAN_SHEETS_REREAD = {5, 6, 7, 17, 18, 22, 23, 28, 29}

WYNN = 'https://www.wynnlasvegas.com/casino/poker'
WYNN_WPT = 'https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf'
WYNN_JAN_SCHEDULE = 'https://cdn.wynnresorts.com/image/upload/v1753296112/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Schedule.pdf'
WYNN_JAN_RULES = 'https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf'
STAY = dict(arrival='2026-11-25', departure='2026-11-28', adults=2, rooms=1, nightly_cap=200)
BOOKING = 'https://www.venetianlasvegas.com/book?adults[]=2&arrival_date=2026-11-25&children[]=0&departure_date=2026-11-28&view=calendar'
ROOM_RATE_SOURCE = 'https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html'
HOTEL_TERMS = 'https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html'
RESORT_FEE = 'https://www.venetianlasvegas.com/resort/resort-fee.html'
# One immutable observation per attempt. Never backfill checkout fields from general policies.
QUOTE_LOG = [dict(**STAY, checked=READ, property='Venetian / Palazzo booking engine',
                  total=None, nightly=None, fee=None, tax=None, parking=None, cancel=None,
                  rate_timestamp=None, url=BOOKING, status='Unverified: booking shell returned; no checkout quote exposed.')]
FINDINGS = [
    ('WPT World Championship', 'Nov 27–Dec 21, 2026',
     'The opening $600 NLH ($400,000 guarantee) allows “Unlimited re-entry for each starting flight” until level 9. Do not treat it as a freezeout.', WYNN_WPT, 'WPT rulebook'),
    ('Wynn Signature Series', 'Jan 11–24, 2027',
     'The schedule is published. The event structures link says “COMING SOON”; entry limits, rebuys and add-ons are unverified. No events promoted.', WYNN_JAN_SCHEDULE, 'January schedule PDF'),
]
WATCH = [
    ('WPT rulebook', WYNN_WPT), ('Wynn January schedule', WYNN_JAN_SCHEDULE),
    ('Wynn January structures placeholder', WYNN_JAN_RULES),
    ('Exact-date Venetian / Palazzo booking lookup', BOOKING),
]
