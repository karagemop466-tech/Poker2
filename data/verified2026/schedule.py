# Official Venetian DeepStack Extravaganza IV schedule, transcribed line by line.
#
# Source A (dates, event #, name, time, structure-sheet link):
#   https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
# Source B (reg closes, chips, level length, guarantee, trophy):
#   https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf
#
# Both retrieved 2026-11-17. Every row below was read off those two official documents.
#
# RECHECK 2026-11-19 (session arena/a9f5847f-poker2): the HTML schedule page
# (Source A) was re-read end to end — all 94 printed rows. No event was added,
# removed, retimed or renamed vs the rows below; every date, start, event
# number, name, guarantee and structure-sheet URL matches. The schedule PDF
# (Source B) was NOT re-read on 2026-11-19, so RETRIEVED stays 2026-11-17.
# Transcript: research/a9f5847f-official-verification-2026-11-19.md
#
# IRREGULARITY X-01: the PDF's DATE column is garbled on 12 rows - a sponsor banner
# ("@PokerAtlas PRO", "@PokerAtlas* TOUR") or a series logo ("LIPS CHAMPIONSHIP ...") is
# printed where the date should be. The date for each of those rows was recovered from the
# official HTML schedule page and is marked `date_from_html=True` below.
#
# Row = (date_iso, weekday, event_no, start, reg_close, guarantee, chips, level,
#        official_name, sheet_no, notes)
#   guarantee None == the official schedule leaves the cell empty.
#   notes "restart" == a continuation of a previous day's event, not a new entry.

SCHEDULE_URL = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
SCHEDULE_PDF = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"
SERIES_URL = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"
POKER_ROOM_URL = "https://www.venetianlasvegas.com/resort/casino/poker.html"
RETRIEVED = "2026-11-17"

ROWS = [
    ("2026-11-16", "Mon",  1, "11:10 AM", "3:40 PM",  "$75,000",  30000, "40", "$300 NO LIMIT HOLD'EM 1A", 10, "flight A"),
    ("2026-11-16", "Mon",  1, "5:10 PM",  "8:40 PM",  "$75,000",  30000, "30", "$300 NO LIMIT HOLD'EM 1B", 9,  "flight B"),
    ("2026-11-17", "Tue",  1, "11:10 AM", "3:40 PM",  "$75,000",  30000, "40", "$300 NO LIMIT HOLD'EM 1C", 10, "flight C"),
    ("2026-11-17", "Tue",  1, "5:10 PM",  "8:40 PM",  "$75,000",  30000, "30", "$300 NO LIMIT HOLD'EM 1D", 9,  "flight D"),
    ("2026-11-18", "Wed",  2, "11:10 AM", "4:55 PM",  "$10,000",  40000, "30", "$300 NO LIMIT HOLD'EM (1DAY)", 5, ""),
    ("2026-11-18", "Wed",  1, "12:00 PM", "",         "",         None,  "40", "$300 NO LIMIT HOLD'EM DAY 2 RESTART", 10, "restart"),
    ("2026-11-19", "Thu",  3, "10:10 AM", "12:25 PM", "",         30000, "20/15", "$200 NLH RACEDAY STACK (1DAY) RACE TO FINISH BEFORE THE RACE", 18, ""),
    ("2026-11-20", "Fri",  4, "10:10 AM", "12:25 PM", "",         30000, "20/15", "$200 NLH RACEDAY STACK (1DAY) RACE TO FINISH BEFORE THE RACE", 18, ""),
    ("2026-11-21", "Sat",  5, "10:10 AM", "12:25 PM", "",         30000, "20/15", "$200 NLH RACEDAY STACK (1DAY) RACE TO FINISH BEFORE THE RACE", 18, ""),
    ("2026-11-22", "Sun",  6, "11:10 AM", "3:40 PM",  "",         30000, "30", "$200 NO LIMIT HOLD'EM (1DAY)", 29, ""),
    ("2026-11-23", "Mon",  7, "11:10 AM", "5:55 PM",  "$75,000",  40000, "40", "$400 NO LIMIT HOLD'EM 1A", 2, "flight A"),
    ("2026-11-23", "Mon",  8, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM (1DAY) PROGRESSIVE KNOCK-OUT BOUNTY (PKO)", 30, ""),
    ("2026-11-24", "Tue",  7, "11:10 AM", "5:55 PM",  "$75,000",  40000, "40", "$400 NO LIMIT HOLD'EM 1B", 2, "flight B"),
    ("2026-11-24", "Tue",  9, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-11-25", "Wed",  7, "11:00 AM", "",         "",         None,  "",   "$400 NO LIMIT HOLD'EM DAY 2 RESTART", 2, "restart"),
    ("2026-11-25", "Wed", 10, "11:10 AM", "4:55 PM",  "$15,000",  40000, "30", "$400 NO LIMIT HOLD'EM (1DAY)", 6, ""),
    ("2026-11-25", "Wed", 11, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-11-26", "Thu", 12, "11:10 AM", "4:55 PM",  "$10,000",  40000, "30", "$300 NO LIMIT HOLD'EM (1DAY)", 5, ""),
    ("2026-11-26", "Thu", 13, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-11-27", "Fri", 14, "11:10 AM", "4:55 PM",  "$30,000",  40000, "30", "$600 NO LIMIT HOLD'EM (1DAY)", 7, ""),
    ("2026-11-27", "Fri", 15, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-11-28", "Sat", 16, "11:10 AM", "4:55 PM",  "$30,000",  40000, "30", "$600 NO LIMIT HOLD'EM BOUNTY (1DAY) $200 BOUNTIES FROM THE START & $500 BOUNTIES ONCE WE REACH THE POSTED PAYOUTS", 11, ""),
    ("2026-11-28", "Sat", 17, "12:10 PM", "4:40 PM",  "$15,000",  30000, "30", "$400 POT LIMIT OMAHA BOUNTY (1DAY)", 26, "date_from_html"),
    ("2026-11-28", "Sat", 18, "5:10 PM",  "9:40 PM",  "$20,000",  25000, "30", "$200 NLH POKERATLAS VALUETOWN BOUNTY (1DAY) POKERATLAS PRO MEMBER $20 RAKE DISCOUNT", 8, "date_from_html"),
    ("2026-11-29", "Sun", 19, "11:10 AM", "5:55 PM",  "$75,000",  40000, "40", "$400 NO LIMIT HOLD'EM 1A", 3, "flight A"),
    ("2026-11-29", "Sun", 20, "12:10 PM", "4:40 PM",  "$10,000",  30000, "30", "$300 POT LIMIT OMAHA DOUBLE BOARD BOMB POT (1DAY)", 22, ""),
    ("2026-11-29", "Sun", 21, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-11-30", "Mon", 19, "11:10 AM", "5:55 PM",  "$75,000",  40000, "40", "$400 NO LIMIT HOLD'EM 1B", 3, "flight B"),
    ("2026-11-30", "Mon", 22, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-12-01", "Tue", 19, "11:10 AM", "5:55 PM",  "$75,000",  40000, "40", "$400 NO LIMIT HOLD'EM 1C", 3, "flight C"),
    ("2026-12-01", "Tue", 23, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-12-02", "Wed", 24, "10:10 AM", "3:55 PM",  "$40,000",  40000, "30", "$600 NO LIMIT HOLD'EM SENIORS (1DAY) MUST BE 50+ YEARS OF AGE TO PARTICIPATE", 17, ""),
    ("2026-12-02", "Wed", 19, "11:00 AM", "",         "",         None,  "",   "$400 NO LIMIT HOLD'EM DAY 2 RESTART", 3, "restart"),
    ("2026-12-02", "Wed", 25, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-12-03", "Thu", 26, "11:10 AM", "3:40 PM",  "$500,000", 40000, "40", "$800 NO LIMIT HOLD'EM 1A", 12, "flight A"),
    ("2026-12-03", "Thu", 27, "12:10 PM", "4:40 PM",  "$25,000",  30000, "30", "$600 BIG O (1DAY)", 28, ""),
    ("2026-12-03", "Thu", 26, "5:10 PM",  "8:40 PM",  "$500,000", 40000, "30", "$800 NO LIMIT HOLD'EM 1B", 13, "flight B"),
    ("2026-12-04", "Fri", 26, "11:10 AM", "3:40 PM",  "$500,000", 40000, "40", "$800 NO LIMIT HOLD'EM 1C", 12, "flight C"),
    ("2026-12-04", "Fri", 26, "5:10 PM",  "8:40 PM",  "$500,000", 40000, "30", "$800 NO LIMIT HOLD'EM 1D", 13, "flight D"),
    ("2026-12-05", "Sat", 26, "11:10 AM", "3:40 PM",  "$500,000", 40000, "40", "$800 NO LIMIT HOLD'EM 1E", 12, "flight E"),
    ("2026-12-05", "Sat", 26, "5:10 PM",  "7:25 PM",  "$500,000", 40000, "20", "$800 NO LIMIT HOLD'EM 1F (TURBO)", 14, "flight F turbo"),
    ("2026-12-06", "Sun", 28, "11:10 AM", "4:55 PM",  "$40,000",  40000, "30", "$600 NO LIMIT HOLD'EM (1DAY)", 7, ""),
    ("2026-12-06", "Sun", 26, "12:00 PM", "",         "",         None,  "",   "$800 NO LIMIT HOLD'EM DAY 2 RESTART", 12, "restart"),
    ("2026-12-06", "Sun", 29, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-07", "Mon", 30, "11:10 AM", "4:55 PM",  "$40,000",  40000, "30", "$600 NO LIMIT HOLD'EM BOUNTY (1DAY) $200 BOUNTIES TO START $500 BOUNTIES IN THE MONEY", 11, ""),
    ("2026-12-07", "Mon", 31, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-08", "Tue", 32, "10:10 AM", "3:55 PM",  "$40,000",  40000, "30", "$600 NO LIMIT HOLD'EM SENIORS (1DAY) MUST BE 50+ YEARS OF AGE TO PARTICIPATE", 17, "date_from_html"),
    ("2026-12-08", "Tue", 33, "4:10 PM",  "6:25 PM",  "2 SEATS",  20000, "20", "$100 NLH LIPS LADIES MILESTONE SATELLITE (1DAY) AWARDS DIRECT ENTRY INTO EVENT #39", 19, "date_from_html"),
    ("2026-12-08", "Tue", 34, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-09", "Wed", 35, "10:10 AM", "2:40 PM",  "$10,000",  40000, "30", "$600 NLH LIPS POKER JINGLE TAG TEAM (1DAY) TAG TEAMS CONSIST OF FEMALE/FEMALE OR FEMALE/MALE", 31, "date_from_html"),
    ("2026-12-09", "Wed", 36, "11:10 AM", "4:55 PM",  "$75,000",  40000, "30", "$800 NO LIMIT HOLD'EM BOUNTY (1DAY) $200 BOUNTIES TO START $500 BOUNTIES IN THE MONEY", 16, "date_from_html"),
    ("2026-12-09", "Wed", 37, "4:10 PM",  "6:25 PM",  "2 SEATS",  20000, "20", "$100 NLH LIPS LADIES MILESTONE SATELLITE (1DAY) AWARDS DIRECT ENTRY INTO EVENT #39", 19, ""),
    ("2026-12-09", "Wed", 38, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-10", "Thu", 39, "10:10 AM", "4:55 PM",  "$40,000",  40000, "40", "$800 NO LIMIT HOLD'EM LIPS LADIES (2DAY) WOMEN IN POKER - MAIN EVENT", 32, "date_from_html"),
    ("2026-12-10", "Thu", 40, "12:10 PM", "4:40 PM",  "$25,000",  30000, "30", "$600 POT LIMIT OMAHA BOUNTY (1DAY)", 27, "date_from_html"),
    ("2026-12-10", "Thu", 41, "4:10 PM",  "6:25 PM",  "2 SEATS",  20000, "20", "$260 NLH MILESTONE SATELLITE (1DAY) AWARDS DIRECT ENTRY INTO EVENT #47", 24, ""),
    ("2026-12-10", "Thu", 42, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-11", "Fri", 39, "10:00 AM", "",         "",         None,  "",   "$800 NO LIMIT HOLD'EM LIPS DAY 2 RESTART PLAY DOWN TO FINAL 7 - STREAMED FINAL TABLE (POKERGO) AT 7:00 PM", 32, "restart"),
    ("2026-12-11", "Fri", 43, "11:10 AM", "4:55 PM",  "$30,000",  40000, "30", "$600 NO LIMIT HOLD'EM LIPS (1DAY) KINGS AND QUEENS BOUNTY - OPEN TO ALL PLAYERS", 33, ""),
    ("2026-12-11", "Fri", 44, "4:10 PM",  "6:25 PM",  "2 SEATS",  20000, "20", "$260 NLH MILESTONE SATELLITE (1DAY) AWARDS DIRECT ENTRY INTO EVENT #47", 24, ""),
    ("2026-12-11", "Fri", 39, "7:00 PM",  "",         "",         None,  "",   "$800 NO LIMIT HOLD'EM LIPS FINAL TABLE STREAMED FINAL TABLE (POKERGO)", 32, "restart"),
    ("2026-12-11", "Fri", 45, "8:10 PM",  "9:55 PM",  "2 SEATS",  20000, "15", "$260 NLH TURBO MILESTONE SATELLITE (1DAY) AWARDS DIRECT ENTRY INTO EVENT #47", 25, ""),
    ("2026-12-12", "Sat", 46, "9:10 AM",  "10:55 AM", "2 SEATS",  20000, "15", "$260 NLH TURBO MILESTONE SATELLITE (1DAY) AWARDS DIRECT ENTRY INTO EVENT #47", 25, "date_from_html"),
    ("2026-12-12", "Sat", 47, "10:10 AM", "4:55 PM",  "$1 MILLION", 40000, "40", "$2,200 NO LIMIT HOLD'EM 1A POKERATLAS CHAMPIONSHIP TITLE EVENT", 21, "date_from_html"),
    ("2026-12-12", "Sat", 48, "12:10 PM", "1:55 PM",  "2 SEATS",  20000, "15", "$260 NLH TURBO MILESTONE SATELLITE (1DAY) AWARDS DIRECT ENTRY INTO EVENT #47", 25, ""),
    ("2026-12-12", "Sat", 47, "6:10 PM",  "11:10 PM", "$1 MILLION", 40000, "30", "$2,200 NO LIMIT HOLD'EM 1B POKERATLAS CHAMPIONSHIP TITLE EVENT", 37, "flight B"),
    ("2026-12-13", "Sun", 49, "10:10 AM", "4:55 PM",  "$300,000", 40000, "40", "$1,100 NO LIMIT HOLD'EM SENIORS 1A MUST BE 50+ YEARS OF AGE TO PARTICIPATE", 20, "date_from_html"),
    ("2026-12-13", "Sun", 47, "1:00 PM",  "",         "",         None,  "",   "$2,200 NO LIMIT HOLD'EM DAY 2 RESTART POKERATLAS CHAMPIONSHIP TITLE EVENT", 21, "restart"),
    ("2026-12-13", "Sun", 50, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-14", "Mon", 49, "10:10 AM", "4:55 PM",  "$300,000", 40000, "40", "$1,100 NO LIMIT HOLD'EM SENIORS 1B MUST BE 50+ YEARS OF AGE TO PARTICIPATE", 20, "date_from_html"),
    ("2026-12-14", "Mon", 47, "11:00 AM", "",         "",         None,  "",   "$2,200 NO LIMIT HOLD'EM DAY 3 RESTART POKERATLAS CHAMPIONSHIP TITLE EVENT STREAMED FINAL TABLE (POKERGO)", 21, "restart"),
    ("2026-12-14", "Mon", 51, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-15", "Tue", 49, "10:00 AM", "",         "",         None,  "",   "$1,100 NO LIMIT HOLD'EM SENIORS DAY 2 RESTART", 20, "restart"),
    ("2026-12-15", "Tue", 52, "11:10 AM", "4:55 PM",  "$75,000",  40000, "30", "$1,100 NO LIMIT HOLD'EM (1DAY) PROGRESSIVE KNOCK-OUT BOUNTY (PKO)", 34, ""),
    ("2026-12-15", "Tue", 53, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-16", "Wed", 54, "11:10 AM", "4:55 PM",  "$50,000",  40000, "30", "$600 NO LIMIT HOLD'EM BOUNTY (1DAY) $200 BOUNTIES TO START $500 BOUNTIES IN THE MONEY", 11, ""),
    ("2026-12-16", "Wed", 55, "5:10 PM",  "9:40 PM",  "$15,000",  25000, "30", "$300 NO LIMIT HOLD'EM BOUNTY (1DAY)", 15, ""),
    ("2026-12-17", "Thu", 56, "10:10 AM", "4:55 PM",  "$500,000", 40000, "40", "$1,100 NO LIMIT HOLD'EM 1A $40 RAKE DISCOUNT FOR ENTRIES BEFORE 10:10 AM", 35, "flight A"),
    ("2026-12-17", "Thu", 57, "12:10 PM", "4:40 PM",  "$25,000",  30000, "30", "$600 POT LIMIT OMAHA DOUBLE BOARD BOMB POT (1DAY)", 23, ""),
    ("2026-12-17", "Thu", 56, "6:10 PM",  "11:10 PM", "$500,000", 40000, "30", "$1,100 NO LIMIT HOLD'EM 1B $40 RAKE DISCOUNT FOR ENTRIES BEFORE 6:10 PM", 36, "flight B"),
    ("2026-12-18", "Fri", 56, "10:10 AM", "4:55 PM",  "$500,000", 40000, "40", "$1,100 NO LIMIT HOLD'EM 1C", 35, "flight C"),
    ("2026-12-18", "Fri", 56, "6:10 PM",  "11:10 PM", "$500,000", 40000, "30", "$1,100 NO LIMIT HOLD'EM 1D", 36, "flight D"),
    ("2026-12-19", "Sat", 56, "10:10 AM", "4:55 PM",  "$500,000", 40000, "40", "$1,100 NO LIMIT HOLD'EM 1E", 35, "flight E"),
    ("2026-12-19", "Sat", 58, "5:10 PM",  "9:40 PM",  "$20,000",  25000, "30", "$200 NLH POKERATLAS VALUETOWN BOUNTY (1DAY) POKERATLAS PRO MEMBER $20 RAKE DISCOUNT", 8, "date_from_html"),
    ("2026-12-20", "Sun", 56, "11:00 AM", "",         "",         None,  "",   "$1,100 NO LIMIT HOLD'EM DAY 2 RESTART", 35, "restart"),
    ("2026-12-20", "Sun", 59, "11:10 AM", "5:55 PM",  "$150,000", 40000, "40", "$600 NO LIMIT HOLD'EM 1A $20 RAKE DISCOUNT FOR ENTRIES BEFORE 11:10 AM", 4, "flight A"),
    ("2026-12-20", "Sun", 60, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-12-21", "Mon", 59, "11:10 AM", "5:55 PM",  "$150,000", 40000, "40", "$600 NO LIMIT HOLD'EM 1B", 4, "flight B"),
    ("2026-12-21", "Mon", 61, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-12-22", "Tue", 59, "11:10 AM", "5:55 PM",  "$150,000", 40000, "40", "$600 NO LIMIT HOLD'EM 1C", 4, "flight C"),
    ("2026-12-22", "Tue", 62, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
    ("2026-12-23", "Wed", 59, "11:00 AM", "",         "",         None,  "",   "$600 NO LIMIT HOLD'EM DAY 2 RESTART", 4, "restart"),
    ("2026-12-23", "Wed", 63, "11:10 AM", "4:55 PM",  "$30,000",  40000, "30", "$600 NO LIMIT HOLD'EM (1DAY)", 7, ""),
    ("2026-12-23", "Wed", 64, "5:10 PM",  "9:40 PM",  "$8,000",   25000, "30", "$200 NO LIMIT HOLD'EM BOUNTY (1DAY)", 1, ""),
]
