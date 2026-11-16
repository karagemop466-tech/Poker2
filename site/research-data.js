/* Research facts and source registry for the static planner. Snapshot: 2026-11-16. */
window.POKER_RESEARCH = {
  snapshot: "2026-11-16",
  events: [
    {
      date: "Nov 18, 2026", time: "11:10 AM", venue: "Venetian",
      name: "Event #02 · $300 NLH · 1 day", buyIn: 300, guarantee: 10000,
      detail: "40,000 starting chips · 30-minute levels · $10K guarantee",
      finding: "Entry limits are not established by the reviewed structure. Do not treat silence as a freezeout rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S5"]
    },
    {
      date: "Nov 19–21, 2026", time: "10:10 AM", venue: "Venetian",
      name: "Events #03–05 · $200 NLH RaceDay Stack", buyIn: 200, guarantee: null,
      detail: "30,000 chips · 20/15-minute levels · registration closes 12:25 PM · no guarantee stated",
      finding: "One-day format is listed, but the reviewed sheet does not confirm a one-entry-only rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S18"]
    },
    {
      date: "Nov 22, 2026", time: "11:10 AM", venue: "Venetian",
      name: "Event #06 · $200 NLH · 1 day", buyIn: 200, guarantee: null,
      detail: "30,000 starting chips · 30-minute levels · no guarantee stated",
      finding: "The structure was reviewed; it does not establish a maximum of one entry per player.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S29"]
    },
    {
      date: "Nov 23, 2026", time: "5:10 PM", venue: "Venetian",
      name: "Event #08 · $200 NLH Progressive Knock-Out Bounty", buyIn: 200, guarantee: 8000,
      detail: "$8K combined prize/bounty guarantee · $25,000 chips · 30-minute levels",
      finding: "The reviewed structure does not confirm a one-entry-only rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S30"]
    },
    {
      date: "Nov 24, 2026", time: "5:10 PM", venue: "Venetian",
      name: "Event #09 · $200 NLH Bounty", buyIn: 200, guarantee: 8000,
      detail: "$8K combined prize/bounty guarantee · $50 bounty · $25,000 chips",
      finding: "The reviewed structure does not confirm a one-entry-only rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S1"]
    },
    {
      date: "Nov 25, 2026", time: "11:10 AM", venue: "Venetian",
      name: "Event #10 · $400 NLH · 1 day", buyIn: 400, guarantee: 15000,
      detail: "$15K guarantee · 40,000 starting chips · 30-minute levels",
      finding: "The reviewed structure does not confirm a one-entry-only rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S6"]
    },
    {
      date: "Nov 26, 2026", time: "11:10 AM", venue: "Venetian",
      name: "Event #12 · $300 NLH · 1 day", buyIn: 300, guarantee: 10000,
      detail: "$10K guarantee · 40,000 starting chips · 30-minute levels",
      finding: "The reviewed structure does not confirm a one-entry-only rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S5"]
    },
    {
      date: "Nov 27, 2026", time: "11:10 AM", venue: "Venetian",
      name: "Event #14 · $600 NLH · 1 day", buyIn: 600, guarantee: 30000,
      detail: "$30K guarantee · 40,000 starting chips · 30-minute levels",
      finding: "The reviewed structure does not confirm a one-entry-only rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S7"]
    },
    {
      date: "Dec 6, 2026", time: "11:10 AM", venue: "Venetian",
      name: "Event #28 · $600 NLH · 1 day", buyIn: 600, guarantee: 40000,
      detail: "$40K guarantee · 40,000 starting chips · 30-minute levels",
      finding: "The reviewed structure does not confirm a one-entry-only rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S7"]
    },
    {
      date: "Dec 23, 2026", time: "11:10 AM", venue: "Venetian",
      name: "Event #63 · $600 NLH · 1 day", buyIn: 600, guarantee: 30000,
      detail: "$30K guarantee · 40,000 starting chips · 30-minute levels",
      finding: "The reviewed structure does not confirm a one-entry-only rule.",
      group: "unconfirmed", badge: "Entry rules not established", sources: ["V_EVENT", "V_S7"]
    },
    {
      date: "Nov 16–17, 2026", time: "11:10 AM / 5:10 PM flights", venue: "Venetian",
      name: "Event #01 · $300 NLH · multi-flight", buyIn: 300, guarantee: 75000,
      detail: "$75K guarantee · flights A/C at 11:10 AM (40-minute levels); B/D at 5:10 PM (30-minute levels)",
      finding: "Multi-flight structure. A Day 2 bagged player cannot play a later flight, but one entry per series is not established.",
      group: "unknown", badge: "Multi-flight · series cap unclear", sources: ["V_EVENT", "V_S10", "V_S9"]
    },
    {
      date: "Daily · 2026 flyer", time: "10:00 AM", venue: "Caesars Palace",
      name: "Daily NLH · $100", buyIn: 100, guarantee: 1000,
      detail: "$1K guarantee · 20,000 starting chips · $50 first-break add-on",
      finding: "Re-entry after elimination is allowed within the first break; add-on is available. Re-entry cap is not stated.",
      group: "spend", badge: "Re-entry + add-on allowed", sources: ["CAESARS_FLYER"]
    },
    {
      date: "Daily · 2026 flyer", time: "2:00 PM", venue: "Caesars Palace",
      name: "Daily NLH · $160", buyIn: 160, guarantee: 1000,
      detail: "$1K guarantee · 20,000 starting chips · $50 first-break add-on · flyer conflicts with marketing article",
      finding: "Re-entry after elimination is allowed within the first break; add-on is available. Re-entry cap is not stated. Prefer the dated flyer over the article’s claim that all four are $100.",
      group: "spend", badge: "Re-entry + add-on allowed", sources: ["CAESARS_FLYER", "CAESARS_TOURNAMENTS"]
    },
    {
      date: "Daily · 2026 flyer", time: "6:00 PM", venue: "Caesars Palace",
      name: "Daily NLH · $100", buyIn: 100, guarantee: 1000,
      detail: "$1K guarantee · 20,000 starting chips · $50 first-break add-on",
      finding: "Re-entry after elimination is allowed within the first break; add-on is available. Re-entry cap is not stated.",
      group: "spend", badge: "Re-entry + add-on allowed", sources: ["CAESARS_FLYER"]
    },
    {
      date: "Daily · 2026 flyer", time: "9:00 PM", venue: "Caesars Palace",
      name: "Daily NLH · $160", buyIn: 160, guarantee: 1000,
      detail: "$1K guarantee · 20,000 starting chips · $50 first-break add-on · flyer conflicts with marketing article",
      finding: "Re-entry after elimination is allowed within the first break; add-on is available. Re-entry cap is not stated. Prefer the dated flyer over the article’s claim that all four are $100.",
      group: "spend", badge: "Re-entry + add-on allowed", sources: ["CAESARS_FLYER", "CAESARS_TOURNAMENTS"]
    },
    {
      date: "Daily", time: "9:00 AM · 11:00 AM · 2:00 PM · 5:00 PM · 8:00 PM · 11:00 PM", venue: "Horseshoe Las Vegas",
      name: "Daily tournament starts · six times listed", buyIn: null, guarantee: null,
      detail: "Official pages reviewed do not provide buy-ins, guarantees, structures, or entry rules for these daily starts.",
      finding: "Start times reported; buy-in and entry policy unknown. No 8:00 AM event confirmed.",
      group: "unknown", badge: "Entry terms unknown", sources: ["CAESARS_TOURNAMENTS", "HORSESHOE_CASINO"]
    },
    {
      date: "Dec 5–12, 2026", time: "11:00 AM (Day 1 schedule)", venue: "Wynn · WPT World Championship",
      name: "WPT Prime Championship · $1,100", buyIn: 1100, guarantee: 5000000,
      detail: "$5M guarantee · multi-flight event",
      finding: "One entry plus one re-entry per starting flight; not single-entry.",
      group: "spend", badge: "One re-entry per flight", sources: ["WPT_SCHEDULE", "WPT_STRUCTURES"]
    },
    {
      date: "Nov 27–Dec 21, 2026", time: "Varies by event", venue: "Wynn · WPT World Championship",
      name: "$600 NLH, $800 NLH, $1,600 NLH, $600 HORSE & $1,600 PLO Mystery Bounty", buyIn: null, guarantee: null,
      detail: "The official structure book permits unlimited re-entry through the stated level deadline in these reviewed events.",
      finding: "Re-entry explicitly allowed; event dates, buy-ins, and deadlines vary by structure.",
      group: "spend", badge: "Unlimited re-entry in reviewed events", sources: ["WPT_SCHEDULE", "WPT_STRUCTURES"]
    },
    {
      date: "Starts Dec 13, 2026", time: "See official flight schedule", venue: "Wynn · WPT World Championship",
      name: "WPT World Championship · $10,400", buyIn: 10400, guarantee: null,
      detail: "The schedule has multiple starting flights; the structure rule is one entry per starting flight, not one entry across the whole series.",
      finding: "Not a one-entry-per-series format. Check the current structure book for flight details.",
      group: "unknown", badge: "One per flight · multiple flights", sources: ["WPT_SCHEDULE", "WPT_STRUCTURES"]
    },
    {
      date: "Daily schedule · verify dates", time: "12:00 PM / 6:00 PM", venue: "Wynn Las Vegas",
      name: "Daily NLH formats · $200 / $240 rebuy / $160", buyIn: null, guarantee: null,
      detail: "Official daily structure sheets cover re-entry, rebuy, and/or add-on options across the formats; the exact mechanic depends on the event.",
      finding: "Not strict single-entry. Dailies can be suspended during Wynn series; WPT-period availability was not established.",
      group: "spend", badge: "Extra-spend rules in structures", sources: ["WYNN_POKER", "WYNN_DAILY_POSTER", "WYNN_DAILY_STRUCTURES"]
    },
    {
      date: "Weekly · exact dates not captured", time: "11:00 AM Friday", venue: "Bellagio",
      name: "Friday NLH · $600", buyIn: 600, guarantee: null,
      detail: "Re-entry allowed through the end of Level 8; current tournament dates were not captured.",
      finding: "Re-entry explicitly permitted; verify that the recurring event is running on your date.",
      group: "spend", badge: "Re-entry allowed · dates unclear", sources: ["BELLAGIO_POKER", "BELLAGIO_FRI"]
    },
    {
      date: "Weekly · exact dates not captured", time: "11:00 AM Sunday", venue: "Bellagio",
      name: "Sunday H.O.R.S.E. · $400", buyIn: 400, guarantee: null,
      detail: "Re-entry allowed through the end of Level 8; current tournament dates were not captured.",
      finding: "Re-entry explicitly permitted; verify that the recurring event is running on your date.",
      group: "spend", badge: "Re-entry allowed · dates unclear", sources: ["BELLAGIO_POKER", "BELLAGIO_SUN"]
    },
    {
      date: "Weekly listing · verify", time: "11:00 AM Saturday (PDF) / current schedule unclear", venue: "Bellagio",
      name: "Saturday NLH · $1,000 / $1,100 discrepancy", buyIn: null, guarantee: 50000,
      detail: "The linked sheet title and listing conflict on the buy-in; a structure detail also conflicts. Re-entry status is not verified.",
      finding: "Do not rely on this row until Bellagio confirms the active schedule and current terms.",
      group: "unknown", badge: "Conflicting listing · rules unclear", sources: ["BELLAGIO_POKER", "BELLAGIO_SAT"]
    },
    {
      date: "Schedule labeled August · current dates unclear", time: "Conflicting / not confirmed", venue: "MGM Grand",
      name: "$120 tournament listing · current event schedule unclear", buyIn: 120, guarantee: null,
      detail: "The reviewed schedule is labeled August and conflicts with other published times; the $120 structure does not establish entry limits.",
      finding: "Current start time and entry policy remain unverified.",
      group: "unknown", badge: "Stale schedule · rules unclear", sources: ["MGM_POKER", "MGM_SCHEDULE"]
    },
    {
      date: "Closed Nov 16, 2026", time: "Not applicable", venue: "SAHARA",
      name: "Poker room closure notice", buyIn: null, guarantee: null,
      detail: "The official room page states the poker room closes on November 16, 2026, despite displaying an old schedule.",
      finding: "Do not use the old schedule as a current event listing.",
      group: "inactive", badge: "Room closure stated", sources: ["SAHARA_POKER"]
    }
  ],
  timeline: [
    { time: "8:00 AM", title: "No verified start", text: "No official 8:00 AM tournament start was confirmed in the sources reviewed.", sources: ["V_EVENT", "CAESARS_TOURNAMENTS", "HORSESHOE_CASINO"] },
    { time: "9:00 AM", title: "Horseshoe daily listing", text: "Earliest recurring start found. Buy-in, structure, and entry rules remain unknown.", sources: ["CAESARS_TOURNAMENTS", "HORSESHOE_CASINO"] },
    { time: "9:10 AM", title: "Venetian satellite · Dec 12", text: "A listed turbo satellite, not a main-field tournament. Entry terms were not established.", sources: ["V_EVENT", "V_SCHED"] },
    { time: "10:00–11:10 AM", title: "Daytime event leads", text: "Caesars daily starts at 10:00 AM; Venetian DSE starts include 10:10 and 11:10 AM. Entry format varies or is unconfirmed.", sources: ["CAESARS_FLYER", "V_EVENT"] }
  ],
  hotels: [
    {
      name: "The Venetian", featured: true, quality: "Forbes Travel Guide · 4-Star",
      relation: "Host property for DeepStack Extravaganza IV. On-property venue; guest-room-to-poker-room walking time not measured.",
      fee: "$55 + applicable tax / night", rate: "Poker rate from $119 / night", total: "No dated total verified",
      note: "Starting rate is conditional on qualifying poker play and availability. Official terms state 13.38% room tax; tax treatment of the resort fee was not independently established.",
      sources: ["V_HOTEL_TERMS", "V_POKER_RATES", "FTG_VENETIAN"]
    },
    {
      name: "The Palazzo", featured: false, quality: "Forbes Travel Guide · 4-Star",
      relation: "Same Venetian resort complex as the DSE poker room; exact guest-room-to-room time not measured.",
      fee: "$55 + applicable tax / night", rate: "Poker rate from $209 / night", total: "No dated total verified",
      note: "Starting rate is conditional on qualifying poker play and availability. It is not a checkout quote or a cost ranking.",
      sources: ["V_HOTEL_TERMS", "V_POKER_RATES", "FTG_PALAZZO"]
    },
    {
      name: "Wynn Las Vegas", featured: false, quality: "Forbes Travel Guide · 4-Star",
      relation: "Host property for the WPT World Championship. On-property venue; exact guest-room-to-poker-room time not measured.",
      fee: "$55 + applicable tax / night", rate: "Date-specific room rate unavailable", total: "No dated total verified",
      note: "The official resort policy confirms the nightly resort fee. The booking page did not return a usable quote in this research pass.",
      sources: ["WYNN_RESORT_INFO", "FTG_WYNN"]
    }
  ],
  questions: [
    { title: "What are the exact trip dates?", text: "Check-in, check-out, and flexibility are required for live hotel totals and a date-matched tournament schedule." },
    { title: "Who is staying, and what room is needed?", text: "Guest count, room type, accessibility, refundable-rate needs, parking, and loyalty rates affect the all-in lodging cost." },
    { title: "What is the poker entry budget?", text: "Set a maximum buy-in and total daily budget before comparing fields or guarantees." },
    { title: "How strict is the entry rule?", text: "The current shortlist stays empty unless an official source confirms no extra entry, re-entry, rebuy, or add-on." },
    { title: "Which games and eligibility are acceptable?", text: "NLH vs. mixed games, bounty formats, satellites, and age or other eligibility limits change what fits." },
    { title: "Does an 8 AM start mean a tournament must begin then?", text: "No verified 8 AM start exists in this source set; the earliest recurring listed tournament start is 9 AM." }
  ],
  sources: {
    V_EVENT: { label: "Venetian DeepStack Extravaganza IV schedule page", publisher: "The Venetian · official event schedule", url: "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html" },
    V_SCHED: { label: "Venetian DSE IV event schedule PDF", publisher: "The Venetian · official PDF", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf" },
    V_S1: { label: "Venetian structure #1 · $200 NLH Bounty", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf" },
    V_S5: { label: "Venetian structure #5 · $300 NLH Events #02 / #12", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf" },
    V_S6: { label: "Venetian structure #6 · $400 NLH Event #10", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf" },
    V_S7: { label: "Venetian structure #7 · $600 NLH Events #14 / #28 / #63", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf" },
    V_S9: { label: "Venetian structure #9 · Event #01 flights B / D", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_9.pdf" },
    V_S10: { label: "Venetian structure #10 · Event #01 flights A / C", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_10.pdf" },
    V_S18: { label: "Venetian structure #18 · $200 RaceDay Stack Events #03–05", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_18.pdf" },
    V_S29: { label: "Venetian structure #29 · $200 NLH Event #06", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_29.pdf" },
    V_S30: { label: "Venetian structure #30 · $200 NLH PKO Event #08", publisher: "The Venetian · official structure", url: "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_30.pdf" },
    CAESARS_FLYER: { label: "Caesars Palace 2026 daily NLH flyer", publisher: "Caesars Palace · official flyer", url: "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf" },
    CAESARS_TOURNAMENTS: { label: "Las Vegas Strip poker tournament information", publisher: "Caesars Entertainment · official article", url: "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip" },
    HORSESHOE_CASINO: { label: "Horseshoe Las Vegas poker room", publisher: "Horseshoe · official casino page", url: "https://www.caesars.com/horseshoe-las-vegas/casino" },
    WPT_SCHEDULE: { label: "WPT World Championship 2026 schedule", publisher: "Wynn · official schedule PDF", url: "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf" },
    WPT_STRUCTURES: { label: "WPT World Championship 2026 structures and rules", publisher: "Wynn · official structure PDF", url: "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf" },
    WYNN_POKER: { label: "Wynn poker room information", publisher: "Wynn · official", url: "https://www.wynnlasvegas.com/casino/poker" },
    WYNN_DAILY_POSTER: { label: "Wynn daily tournament poster", publisher: "Wynn · official PDF", url: "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf" },
    WYNN_DAILY_STRUCTURES: { label: "Wynn daily tournament structures", publisher: "Wynn · official PDF", url: "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf" },
    BELLAGIO_POKER: { label: "Bellagio poker room schedule information", publisher: "Bellagio · official", url: "https://bellagio.mgmresorts.com/en/casino/poker.html" },
    BELLAGIO_FRI: { label: "Bellagio Friday $600 NLH structure", publisher: "Bellagio · official PDF", url: "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf" },
    BELLAGIO_SUN: { label: "Bellagio Sunday $400 H.O.R.S.E. structure", publisher: "Bellagio · official PDF", url: "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf" },
    BELLAGIO_SAT: { label: "Bellagio Saturday NLH listing and structure", publisher: "Bellagio · official PDF", url: "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf" },
    MGM_POKER: { label: "MGM Grand poker room page", publisher: "MGM Grand · official", url: "https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html" },
    MGM_SCHEDULE: { label: "MGM Grand weekly tournament schedule", publisher: "MGM Grand · official PDF", url: "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf" },
    SAHARA_POKER: { label: "SAHARA poker room and closure notice", publisher: "SAHARA · official", url: "https://www.saharalasvegas.com/casino/sahara-poker-room/1000" },
    V_HOTEL_TERMS: { label: "Venetian hotel terms and conditions", publisher: "The Venetian · official", url: "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html" },
    V_POKER_RATES: { label: "Venetian poker suite rates and play requirements", publisher: "The Venetian · official", url: "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html" },
    WYNN_RESORT_INFO: { label: "Wynn resort information and resort fee", publisher: "Wynn · official", url: "https://www.wynnlasvegas.com/about-us/resort-information" },
    FTG_VENETIAN: { label: "The Venetian Resort Las Vegas · 2026 listing", publisher: "Forbes Travel Guide", url: "https://www.forbestravelguide.com/hotels/las-vegas-nevada/the-venetian-resort-las-vegas" },
    FTG_PALAZZO: { label: "The Palazzo at The Venetian Resort · 2026 listing", publisher: "Forbes Travel Guide", url: "https://www.forbestravelguide.com/hotels/las-vegas-nevada/the-palazzo-at-the-venetian-resort-las-vegas" },
    FTG_WYNN: { label: "Wynn Las Vegas · 2026 listing", publisher: "Forbes Travel Guide", url: "https://www.forbestravelguide.com/hotels/las-vegas-nevada/wynn-las-vegas" }
  }
};
