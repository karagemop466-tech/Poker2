#!/usr/bin/env python3
"""Regression guards for factual distinctions and dynamic review reporting."""
import json
from collections import Counter

import build2026 as site


def main():
    events = site.build_events()
    by_number = {event['event_no']: event for event in events}
    assert by_number[39]['group'] == 'multiday', 'a Day 2 continuation is not a starting flight'
    assert not by_number[39]['flight_rule']
    assert by_number[7]['group'] == 'multiflight' and by_number[7]['flight_rule']
    for event in events:
        if event['group'] == 'multiflight':
            assert event['flight_rule'], event['event_no']
        assert not event['single_entry_confirmed'], event['event_no']

    flags = site.contentmod.FLAGS + site.fresh.FLAGS
    ids = Counter(item['id'] for item in flags)
    assert all(count == 1 for count in ids.values()), f'duplicate flag IDs: {ids}'
    report = site.CHECKS_META or {}
    runs = report.get('runs') or []
    bad = [row for row in (runs[0].get('results', []) if runs else []) if row.get('change') == 'fetch error']
    monitor = [f for f in flags if f['id'] == 'F-MONITOR']
    assert bool(monitor) == bool(bad), 'dynamic monitor flag must reflect actual results'
    if bad:
        assert f"{len(bad)} of {len(runs[0]['results'])}" in monitor[0]['detail']
    saturday = next(e for e in site.othermod.BELLAGIO_SCHEDULE['events'] if e['day'] == 'Saturdays')
    assert saturday['buy_in'] is None and saturday['buy_in_conflict']
    assert not any(name == 'Re-entry' for name, _ in saturday['quotes'])
    assert 'does not state that re-entry rule' in site.othermod.BELLAGIO_SCHEDULE['verdict']

    stored = json.load(open('data/verified2026/dataset.json', encoding='utf-8'))
    assert next(e for e in stored['events'] if e['event_no'] == 39)['group'] == 'multiday'
    print('Evidence checks: continuation vs flights, unique flags, monitor counts, Saturday conflict, no inferred freezeouts.')


if __name__ == '__main__':
    main()
