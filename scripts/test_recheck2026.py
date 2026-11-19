"""Offline regression tests: failed fetches and subsequent runs must not erase evidence."""
import unittest
import recheck2026 as m

class MonitorTests(unittest.TestCase):
    def test_baseline_survives_error_and_key_rename(self):
        history = [dict(checked='later', results=[dict(url='u', key='new', hash=None, change='fetch error')]),
                   dict(checked='earlier', results=[dict(url='u', key='old', hash='a', change='first check')])]
        self.assertEqual(m.source_state(history)['u']['last_hash'], 'a')
    def test_review_survives_unchanged_and_error(self):
        history = [dict(results=[dict(url='u', hash=None, change='fetch error')]),
                   dict(results=[dict(url='u', hash='b', change='unchanged')]),
                   dict(results=[dict(url='u', hash='b', change='CHANGED')])]
        self.assertTrue(m.source_state(history)['u']['review_required'])
    def test_durable_state_and_explicit_review(self):
        h = [dict(results=[dict(url='u', hash='b', change='CHANGED')])]
        self.assertFalse(m.source_state(h, {'u': {'review_required': False}})['u']['review_required'])
        self.assertEqual(m.source_state([], {'u': {'last_hash': 'a'}})['u']['last_hash'], 'a')
    def test_reviewed_hash_clears_only_the_exact_content_version(self):
        changed = [dict(checked='today', results=[dict(url='u', hash='b', change='CHANGED')])]
        self.assertFalse(m.source_state(changed, reviewed={'u': 'b'})['u']['review_required'])
        self.assertTrue(m.source_state(changed, reviewed={'u': 'old'})['u']['review_required'])
        changed_again = [
            dict(checked='later', results=[dict(url='u', hash='c', change='CHANGED')]),
            dict(checked='today', results=[dict(url='u', hash='b', change='CHANGED')]),
        ]
        state = m.source_state(changed_again, reviewed={'u': 'b'})['u']
        self.assertEqual(state['last_hash'], 'c')
        self.assertTrue(state['review_required'])
    def test_prior_monitor_metadata_is_preserved(self):
        history = [dict(checked='now', results=[dict(url='u', hash='b', change='unchanged', last_changed='earlier')])]
        self.assertTrue(m.source_state(history)['u']['review_required'])
        self.assertEqual(m.prior_observations(history), ({'u':'b'}, {'u':'earlier'}))
    def test_every_hotel_field_source_is_registered(self):
        urls = {url for label, url in m.sources().values()}
        for hotel in m.hotelsmod.HOTELS:
            for key, value in hotel.items():
                if key.endswith('_src') and value:
                    self.assertIn(value, urls)
    def test_reject_fake_pdf(self):
        with self.assertRaises(ValueError):
            m.content_hash('https://official.test/a.pdf', b'<html>Access denied</html>')
        self.assertTrue(m.content_hash('https://official.test/a.pdf', b'%PDF-1.7\nfixture')[0])
    def test_reject_soft_errors(self):
        for raw in (b'', b'<title>Page not found</title>', b'<title>Just a moment...</title>',
                    b'IT SEEMS THIS PAGE HAS CHECKED OUT'):
            with self.assertRaises(ValueError):
                m.content_hash('https://official.test/', raw)
    def test_real_html_normalises(self):
        self.assertEqual(m.content_hash('https://official.test/', b'<h1>Rules</h1>')[0],
                         m.content_hash('https://official.test/', b' Rules ')[0])

if __name__ == '__main__':
    unittest.main()
