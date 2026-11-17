# Hotel data. Every value carries the official page it was read from and the date it was read.
# Nothing is inferred: a cell the organiser does not publish stays None and is listed on the
# Flagged for review page.
#
# Retrieved in THIS session (2026-11-17) unless the entry says otherwise.

ROOM_TAX_DEFAULT = 13.38   # Clark County room tax, per the official Venetian hotel terms.
ROOM_TAX_SOURCE = "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"
ROOM_TAX_NOTE = ("13.38% is printed in the official Venetian hotel terms, which were re-read first-hand "
                 "on 2026-11-17: \u201cDaily rates do not include the applicable Clark County Room Tax of "
                 "13.38%.\u201d The county's own guide is cited as the authority for the levy itself but "
                 "was not re-read in this session. See flag F-07.")

# id, name, address, official booking page, resort fee, tax %, parking, cancellation, quality note
HOTELS = [
    dict(
        id="venetian", name="The Venetian Resort",
        addr="3355 S Las Vegas Blvd, Las Vegas, NV 89109",
        book="https://www.venetianlasvegas.com/book",
        resort_fee=55, resort_fee_note="$55 per night, plus tax. Includes Canyon Ranch fitness for two, in-suite internet, boarding-pass printing, local/toll-free calls, PressReader.",
        resort_fee_src="https://www.venetianlasvegas.com/resort/resort-fee.html",
        resort_fee_checked="2026-11-17",
        tax_pct=13.38,
        tax_src=ROOM_TAX_SOURCE,
        tax_checked="2026-11-17",
        poker_rate=119,
        poker_rate_note=("Poker suite rate starts as low as $119 at The Venetian (and $209 at The Palazzo). "
                         "Book by phone 866.255.8936, code EPOKR25. Conditional: six hours of active live cash "
                         "play OR a buy-in to a $300-or-higher tournament for each night stayed, completed before "
                         "2 a.m. on the last night; otherwise the night is re-rated to the prevailing rate. "
                         "Cannot be combined with other promotional rates. Blackout dates may apply."),
        poker_rate_src="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
        poker_rate_checked="2026-11-17",
        parking="Registered hotel guests $20/day. Non-registered guests $20 Mon-Thu, $25 Fri-Sun; valet $40/day. Free self-parking for Venetian Rewards Sapphire and above.",
        parking_src="https://www.venetianlasvegas.com/resort/casino/poker.html",
        parking_note="The official poker page read today additionally states: non-registered hotel guests who play three hours or more in tournaments or cash games receive complimentary self-parking.",
        cancel=("No cancellation deadline is printed for the poker suite rate. The general hotel terms "
                "say a deposit (first night or entire stay, depending on the offer) is billed at "
                "confirmation, that prepaid offers are non-cancellable and non-refundable unless the "
                "offer says otherwise, and that check-out before the scheduled departure date costs "
                "an additional $100 plus tax."),
        cancel_src="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
        cancel_checked="2026-11-17",
        cancel_type="general hotel terms; not specific to the poker rate",
        extra_guest_fee="$50 per night for each additional guest 13 or older above double occupancy (Prestige: $50 for 5-20, $75 for 21+).",
        early_checkout_fee="$100 plus tax",
        quality="No official star or diamond rating is published by the resort for standard suites.",
        dated_total=None,
    ),
    dict(
        id="palazzo", name="The Palazzo",
        addr="3325 S Las Vegas Blvd, Las Vegas, NV 89109",
        book="https://www.venetianlasvegas.com/book",
        resort_fee=55, resort_fee_note="Same resort-fee page as The Venetian: $55 per night, plus tax.",
        resort_fee_src="https://www.venetianlasvegas.com/resort/resort-fee.html",
        resort_fee_checked="2026-11-17",
        tax_pct=13.38,
        tax_src=ROOM_TAX_SOURCE,
        tax_checked="2026-11-17",
        poker_rate=209,
        poker_rate_note="Poker suite rate starts as low as $209 at The Palazzo. Same code EPOKR25 and the same per-night qualifying-play condition.",
        poker_rate_src="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
        poker_rate_checked="2026-11-17",
        parking="Same resort parking terms as The Venetian.",
        parking_src="https://www.venetianlasvegas.com/resort/casino/poker.html",
        parking_note=None,
        cancel=("Same terms as The Venetian; no poker-rate-specific cancellation deadline is printed."),
        cancel_src="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
        cancel_checked="2026-11-17",
        cancel_type="general hotel terms; not specific to the poker rate",
        extra_guest_fee="$50 per night for each additional guest 13 or older above double occupancy.",
        early_checkout_fee="$100 plus tax",
        quality="No official star or diamond rating is published by the resort for standard suites.",
        dated_total=None,
    ),
    dict(
        id="wynn", name="Wynn Las Vegas",
        addr="3131 S Las Vegas Blvd, Las Vegas, NV 89109",
        book="https://www.wynnlasvegas.com/",
        resort_fee=55, resort_fee_note=None,
        resort_fee_src="https://www.wynnlasvegas.com/about-us/resort-information",
        resort_fee_checked="2026-11-16",
        tax_pct=None,
        poker_rate=None, poker_rate_note=None, poker_rate_src=None, poker_rate_checked=None,
        parking="Complimentary self-parking for up to two vehicles, included in the resort fee.",
        parking_src="https://www.wynnlasvegas.com/about-us/resort-information",
        parking_note=None,
        cancel=("No cancellation deadline is printed on the resort-information page. A valid credit card is "
                "required to confirm a reservation and one night's room rate and tax is charged at booking; "
                "the page does not state whether that deposit is refundable."),
        cancel_src="https://www.wynnlasvegas.com/about-us/resort-information",
        cancel_checked="2026-11-17",
        cancel_type="deposit terms only; refund window not published",
        extra_guest_fee=None,
        early_checkout_fee=None,
        quality="No official star or diamond rating read.",
        dated_total=None,
    ),
    dict(
        id="encore", name="Encore at Wynn Las Vegas",
        addr="3121 S Las Vegas Blvd, Las Vegas, NV 89109",
        book="https://www.wynnlasvegas.com/",
        resort_fee=55, resort_fee_note=None,
        resort_fee_src="https://www.wynnlasvegas.com/about-us/resort-information",
        resort_fee_checked="2026-11-16",
        tax_pct=None,
        poker_rate=None, poker_rate_note=None, poker_rate_src=None, poker_rate_checked=None,
        parking="Complimentary self-parking for up to two vehicles, included in the resort fee.",
        parking_src="https://www.wynnlasvegas.com/about-us/resort-information",
        parking_note=None,
        cancel=("No cancellation deadline is printed on the resort-information page. A valid credit card is "
                "required to confirm a reservation and one night's room rate and tax is charged at booking; "
                "the page does not state whether that deposit is refundable."),
        cancel_src="https://www.wynnlasvegas.com/about-us/resort-information",
        cancel_checked="2026-11-17",
        cancel_type="deposit terms only; refund window not published",
        extra_guest_fee=None,
        early_checkout_fee=None,
        quality="No official star or diamond rating read.",
        dated_total=None,
    ),
    dict(
        id="bellagio", name="Bellagio",
        addr="3600 S Las Vegas Blvd, Las Vegas, NV 89109",
        book="https://bellagio.mgmresorts.com/en.html",
        resort_fee=55, resort_fee_note=None,
        resort_fee_src="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
        resort_fee_checked="2026-11-16",
        tax_pct=None,
        poker_rate=None, poker_rate_note=None, poker_rate_src=None, poker_rate_checked=None,
        parking=None, parking_src=None, parking_note="Not stated on the pages read.",
        cancel=("First night's deposit is fully refundable if Room Reservations (888.987.6667) receives "
                "cancellation at least 72 hours before arrival, unless the booked offer excludes it. "
                "Later cancellation or a no-show forfeits the first night's deposit. A complimentary "
                "first night cancelled late costs $165 mid-week or $200 for a Friday/Saturday arrival."),
        cancel_src="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
        cancel_checked="2026-11-17",
        cancel_type="general reservation terms",
        extra_guest_fee="$50 plus tax per occupant per night above 2 occupants.",
        early_checkout_fee=None,
        quality="No official star or diamond rating read.",
        dated_total=None,
    ),
    dict(
        id="mgm-grand", name="MGM Grand",
        addr="3799 S Las Vegas Blvd, Las Vegas, NV 89109",
        book="https://mgmgrand.mgmresorts.com/en.html",
        resort_fee=50, resort_fee_note=None,
        resort_fee_src="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
        resort_fee_checked="2026-11-16",
        tax_pct=None,
        poker_rate=None, poker_rate_note=None, poker_rate_src=None, poker_rate_checked=None,
        parking=None, parking_src=None, parking_note="Not stated on the pages read.",
        cancel=("First night's deposit is fully refundable if Room Reservations (877.880.0880) receives "
                "cancellation at least 72 hours before arrival, unless the booked offer excludes it. "
                "Later cancellation or a no-show forfeits the first night's deposit. A complimentary "
                "first night cancelled late costs $110 mid-week or $155 for a Friday/Saturday/Sunday arrival."),
        cancel_src="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
        cancel_checked="2026-11-17",
        cancel_type="general reservation terms",
        extra_guest_fee="$40 plus tax per occupant per night above 2 occupants.",
        early_checkout_fee=None,
        quality="No official star or diamond rating read.",
        dated_total=None,
    ),
    dict(
        id="caesars-palace", name="Caesars Palace",
        addr="3570 S Las Vegas Blvd, Las Vegas, NV 89109",
        book="https://www.caesars.com/caesars-palace",
        resort_fee=None, resort_fee_note=None,
        resort_fee_src="https://www.caesars.com/caesars-palace/casino",
        resort_fee_checked="2026-11-16",
        tax_pct=None,
        poker_rate=None, poker_rate_note=None, poker_rate_src=None, poker_rate_checked=None,
        parking=None, parking_src=None, parking_note="The hotel page says only 'Valet and self-parking available'; no rate is printed.",
        cancel=("The hotel page advertises 'FREE 48-Hour Cancellation*' with an asterisk and does not "
                "print the condition. No deposit or forfeiture terms are published on the page read."),
        cancel_src="https://www.caesars.com/caesars-palace/hotel",
        cancel_checked="2026-11-17",
        cancel_type="headline claim only; conditions not published",
        extra_guest_fee=None,
        early_checkout_fee=None,
        quality=("No official star or diamond rating read for the standard rooms. The property states that "
                 "its separate Villa product holds a AAA Five Diamond designation."),
        dated_total=None,
    ),
    dict(
        id="horseshoe", name="Horseshoe Las Vegas",
        addr="3645 S Las Vegas Blvd, Las Vegas, NV 89109",
        book="https://www.caesars.com/horseshoe-las-vegas",
        resort_fee=None, resort_fee_note=None,
        resort_fee_src="https://www.caesars.com/horseshoe-las-vegas/casino",
        resort_fee_checked="2026-11-16",
        tax_pct=None,
        poker_rate=None, poker_rate_note=None, poker_rate_src=None, poker_rate_checked=None,
        parking=None, parking_src=None, parking_note="The hotel page says only 'Valet and self-parking available'; no rate is printed.",
        cancel=("The hotel page advertises 'FREE 48-Hour Cancellation*' with an asterisk and does not "
                "print the condition. No deposit or forfeiture terms are published on the page read."),
        cancel_src="https://www.caesars.com/horseshoe-las-vegas/hotel",
        cancel_checked="2026-11-17",
        cancel_type="headline claim only; conditions not published",
        extra_guest_fee=None,
        early_checkout_fee=None,
        quality="No official star or diamond rating read.",
        dated_total=None,
    ),
]

# The dated rate log. One line per reading, newest first. This is the whole point of the
# "rates are a log, not a value" requirement: a rate without a date and a source is not data.
RATE_LOG = [
    ("2026-11-17", "venetian", "resort_fee", "$55 per night + tax",
     "https://www.venetianlasvegas.com/resort/resort-fee.html", "read this session"),
    ("2026-11-17", "venetian", "resort_fee", "$55 plus tax per night, payable upon check-in",
     "https://www.venetianlasvegas.com/resort/resort-fee.html",
     "re-read first-hand 2026-11-17 by arena/7be88b38-poker2; the page lists the inclusions "
     "(Canyon Ranch fitness for two, in-suite internet, boarding-pass printing, local/toll-free calls, PressReader)"),
    ("2026-11-17", "venetian", "room_tax", "13.38% transient lodging tax, resort-hotel rate (Paradise Commercial Zone)",
     "https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf",
     "county licence register row 'Venetian Resort Hotel Casino / Palazzo Resort Hotel Casino ... 13.38% ... "
     "Resort Hotel (PGC)', read 2026-11-17; see flag F-15 on the document's own date"),
    ("2026-11-17", "venetian", "poker_rate", "from $119 (Venetian) / $209 (Palazzo), code EPOKR25",
     "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html", "read this session"),
    ("2026-11-17", "venetian", "qualifying_play", "6 hrs live cash OR $300+ tournament buy-in, per night, before 2 a.m. last night",
     "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html", "read this session"),
    ("2026-11-17", "venetian", "parking", "Registered guests $20/day; 3+ hrs play earns free self-parking for non-guests",
     "https://www.venetianlasvegas.com/resort/casino/poker.html", "read this session"),
    ("2026-11-17", "venetian", "room_tax_rate", "13.38% (re-read first-hand: \u201cClark County Room Tax of 13.38%\u201d)",
     ROOM_TAX_SOURCE, "this session re-read the page and confirms the figure; F-07 narrowed to the county levy only"),
    ("2026-11-17", "venetian", "cancellation", "no poker-rate deadline printed; prepaid offers non-cancellable/non-refundable; early check-out $100 + tax",
     "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html", "read this session (F-06 partly resolved)"),
    ("2026-11-17", "venetian", "extra_guest_fee", "$50/night per additional guest 13+ above double occupancy",
     "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html", "read this session; matters for occupancy above 2"),
    ("2026-11-17", "wynn", "resort_fee", "$55 plus tax per night, re-read first-hand", "https://www.wynnlasvegas.com/about-us/resort-information",
     "this session re-read the page; the 2026-11-16 figure is confirmed"),
    ("2026-11-17", "bellagio", "resort_fee", "$55.00 plus applicable tax, re-read first-hand", "https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
     "this session re-read the page; the 2026-11-16 figure is confirmed"),
    ("2026-11-17", "bellagio", "cancellation", "72 hours before arrival, first night's deposit refundable",
     "https://bellagio.mgmresorts.com/en/terms-and-conditions.html", "read this session (resolves F-06 for Bellagio)"),
    ("2026-11-17", "mgm-grand", "resort_fee", "$50.00 plus applicable tax, re-read first-hand", "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
     "this session re-read the page; the 2026-11-16 figure is confirmed"),
    ("2026-11-17", "mgm-grand", "cancellation", "72 hours before arrival, first night's deposit refundable",
     "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html", "read this session (resolves F-06 for MGM Grand)"),
    ("2026-11-17", "caesars-palace", "cancellation", "\u201cFREE 48-Hour Cancellation*\u201d headline only; conditions not published",
     "https://www.caesars.com/caesars-palace/hotel", "read this session; resort fee still not published on the pages read"),
    ("2026-11-17", "horseshoe", "cancellation", "\u201cFREE 48-Hour Cancellation*\u201d headline only; conditions not published",
     "https://www.caesars.com/horseshoe-las-vegas/hotel", "read this session; resort fee still not published on the pages read"),
    ("2026-11-16", "venetian", "room_tax_rate", "13.38%",
     ROOM_TAX_SOURCE, "read by an earlier session; see flag F-07"),
    ("2026-11-16", "wynn", "resort_fee", "$55",
     "https://www.wynnlasvegas.com/about-us/resort-information", "read by an earlier session"),
    ("2026-11-16", "encore", "resort_fee", "$55",
     "https://www.wynnlasvegas.com/about-us/resort-information", "read by an earlier session"),
    ("2026-11-16", "bellagio", "resort_fee", "$55",
     "https://bellagio.mgmresorts.com/en/terms-and-conditions.html", "read by an earlier session"),
    ("2026-11-16", "mgm-grand", "resort_fee", "$50",
     "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html", "read by an earlier session"),
    ("2026-11-17", "ALL", "dated_checkout_total", "no dated quote captured",
     None, "Official booking engines render rates with JavaScript; no dated checkout total could be read. See F-05."),
    ("2026-11-17", "ALL", "cancellation_deadline", "partial: Bellagio and MGM Grand publish 72 h; Caesars properties publish a 48 h headline; Venetian/Palazzo publish prepaid and early-checkout terms; Wynn publishes deposit terms only",
     None, "See F-06 for the per-property status."),
]
