#!/usr/bin/env python3
"""Offline fixtures: source history and official schedule parser must fail closed."""
import build2026 as site
import recheck2026 as monitor

url = site.sched.SCHEDULE_URL
rows = site.sched.ROWS

def fixture(selected):
    from datetime import date

    return ('<table>' + ''.join(
        '<tr><td>%s</td><td>%s</td><td>%s</td><td>Event</td><td><a href="/docs/structure_%d.pdf">View</a></td><td>Results</td></tr>'
        % (date.fromisoformat(r[0]).strftime('%A, %B %d, %Y'), r[3], r[2], r[9])
        for r in selected) + '</table>').encode()

assert monitor.schedule_diff(fixture(rows)) == dict(state='rows match', count=94, added=[], removed=[])
assert monitor.schedule_diff(fixture(rows[:-1]))['removed'] == [(rows[-1][0], rows[-1][3], rows[-1][2], rows[-1][9])]
assert monitor.schedule_diff(b'<title>Access denied</title>')['state'] == 'unreadable schedule table'
a = b'<a href="schedule.pdf">Official schedule</a>'
b = b'<a href="other.pdf">Official schedule</a>'
assert monitor.content_hash(url, a)[0] != monitor.content_hash(url, b)[0]
try:
    monitor.content_hash(site.sched.SCHEDULE_PDF, a)
except ValueError:
    pass
else:
    raise AssertionError('HTML served instead of a PDF must not be treated as a valid PDF baseline')

first = dict(checked='2026-11-17', results=[dict(url=url, key='before', change='first check', hash='a')])
changed = dict(checked='2026-11-18', results=[dict(url=url, key='after', change='CHANGED', hash='b', hash_method='method')])
error = dict(checked='2026-11-19', results=[dict(url=url, key='after', change='fetch error', hash=None)])
assert monitor.prior_successes([error, changed, first])[url]['hash'] == 'b'
assert monitor.review_state([error, changed, first]) == {url: '2026-11-18'}
proof = dict(url=url, hash='b', hash_method='method', reviewed_at='2026-11-19', reviewer='test', note='read exact version')
assert monitor.review_state([error, changed, first], [proof]) == {}
assert monitor.review_state([error, changed, first], [dict(proof, hash='a')]) == {url: '2026-11-18'}
assert monitor.review_state([error, changed, first], {url: 'b'}) == {url: '2026-11-18'}
quiet = dict(checked='2026-11-19', results=[dict(url=url, key='after', change='unchanged', hash='b', review_since='2026-11-18')])
assert monitor.review_state([quiet]) == {url: '2026-11-18'}

proof = dict(max_entries=1, scope='whole event', reentry=False, rebuy=False, addon=False,
             paid_advantage=False, quote='One entry per person across the event; no re-entry, rebuy, add-on or paid advantage.')
sheet = dict(url=url, retrieved='2026-11-19')
assert site.confirmed_freezeout(dict(sheet, entry_policy=proof))
assert not site.confirmed_freezeout(dict(sheet, single_entry_confirmed=True))
for field, bad in [('scope', 'per flight'), ('max_entries', True), ('reentry', True), ('rebuy', None),
                   ('addon', True), ('paid_advantage', None), ('quote', '')]:
    assert not site.confirmed_freezeout(dict(sheet, entry_policy=dict(proof, **{field: bad}))), field

assert not any(day['primary'] or day['fallbacks'] for day in site.build_days(site.build_events()))
first = dict(start_m=600)
later = dict(start_m=660, reg_close_m=690, reg_close='11:30 AM')
assert site.sequence(first, later)[0] == 'conditional fallback'
assert site.sequence(dict(first, finish_m=720), later)[0] == 'cannot be sequenced'
assert site.sequence(dict(first, finish_m=650), later)[0] == 'no published overlap'
assert site.sequence(first, dict(later, reg_close_m=None))[0] == 'unknown'
print('Refresh fixtures: 94 row keys, changed PDF link, old baseline across errors, and strict schedule gates pass.')
