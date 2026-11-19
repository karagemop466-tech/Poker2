#!/usr/bin/env python3
"""Offline regression tests for change warnings, binary hashes and monitoring gaps."""
import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import build_monitor_registry
import build_site
import monitor
import recheck2026
from source_monitoring import legacy_pending, review_state


class SourceMonitoringTests(unittest.TestCase):
    def test_change_persists_after_unchanged_error_and_recovers_after_exact_review(self):
        url = "https://www.venetianlasvegas.com/test.pdf"
        with tempfile.TemporaryDirectory() as d:
            output = str(Path(d) / "checks.json")
            responses = [b"%PDF-1.0 A", b"%PDF-1.0 B", b"%PDF-1.0 B",
                         TimeoutError("test timeout"), b"%PDF-1.0 B", b"%PDF-1.0 B", b"%PDF-1.0 C"]
            reviews = []

            def fetch(_url):
                result = responses.pop(0)
                if isinstance(result, Exception):
                    raise result
                return 200, result, url

            with mock.patch.object(recheck2026, "OUT", output), \
                 mock.patch.object(recheck2026, "sources", return_value={"TEST": ("Test", url)}), \
                 mock.patch.object(recheck2026, "fetch", side_effect=fetch), \
                 mock.patch.object(recheck2026, "load_reviews", side_effect=lambda: reviews), \
                 contextlib.redirect_stdout(io.StringIO()):
                def run():
                    # A single-source failure is normally blocked to avoid a networkless overwrite.
                    with mock.patch.object(recheck2026.sys, "argv", ["recheck2026.py", "--allow-no-network"]):
                        self.assertEqual(recheck2026.main(), 0)
                    return json.loads(Path(output).read_text())["runs"][0]["results"][0]

                self.assertEqual(run()["change"], "first check")
                moved = run()
                self.assertEqual(moved["change"], "CHANGED")
                self.assertTrue(moved["review_pending"])
                same = run()
                self.assertEqual(same["change"], "unchanged")
                self.assertTrue(same["review_pending"])
                failed = run()
                self.assertEqual(failed["change"], "fetch error")
                self.assertTrue(failed["review_pending"])
                self.assertEqual(failed["last_success_hash"], moved["hash"])
                recovered = run()
                self.assertEqual(recovered["change"], "unchanged")
                self.assertTrue(recovered["review_pending"])
                reviews.append(dict(url=url, hash=recovered["hash"], hash_method="raw PDF bytes",
                                    reviewed_at="2026-11-19", reviewer="test", note="read official sheet"))
                self.assertFalse(run()["review_pending"])
                self.assertTrue(run()["review_pending"])  # a new version cannot use the old review

    def test_root_monitor_persists_legacy_change_and_records_exact_review(self):
        url = "https://www.venetianlasvegas.com/test.pdf"
        rec = {"url": url, "status": "new"}
        monitor.update_success(rec, b"%PDF-1.0 A", 200, "2026-11-17", [])
        monitor.update_success(rec, b"%PDF-1.0 B", 200, "2026-11-18", [])
        self.assertTrue(rec["review_pending"])
        monitor.update_success(rec, b"%PDF-1.0 B", 200, "2026-11-19", [])
        self.assertEqual(rec["status"], "unchanged")
        self.assertTrue(rec["review_pending"])
        pending, _ = review_state(rec, False, "2026-11-20", url, None, None, [])
        self.assertTrue(pending)  # failed fetch
        wrong_review = dict(url=url, hash="wrong", hash_method=rec["hash_method"],
                            reviewed_at="2026-11-19", reviewer="test", note="read")
        monitor.update_success(rec, b"%PDF-1.0 B", 200, "2026-11-20", [wrong_review])
        self.assertTrue(rec["review_pending"])
        wrong_review["hash"] = rec["sha256"]
        monitor.update_success(rec, b"%PDF-1.0 B", 200, "2026-11-20", [wrong_review])
        self.assertFalse(rec["review_pending"])
        self.assertFalse(legacy_pending(rec))  # legacy changed_on must not resurrect it

    def test_raw_pdf_hash_and_snapshot_names(self):
        # Both invalid bytes used to become the same Unicode replacement character.
        self.assertEqual(monitor.norm_text(b"%PDF-\xff"), monitor.norm_text(b"%PDF-\xfe"))
        self.assertNotEqual(monitor.content_digest("https://example.com/a.pdf", b"%PDF-\xff")[0],
                            monitor.content_digest("https://example.com/a.pdf", b"%PDF-\xfe")[0])
        a = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf"
        b = a.replace("_1.pdf", "_2.pdf")
        self.assertNotEqual(monitor.slug(a), monitor.slug(b))

    def test_lossy_pdf_migration_is_not_falsely_reported_as_a_new_change(self):
        import hashlib
        raw = b"%PDF-1.0 \xff A"
        old = hashlib.sha256(monitor.norm_text(raw).encode()).hexdigest()
        rec = {"url": "https://example.com/a.pdf", "sha256": old, "status": "unchanged"}
        monitor.update_success(rec, raw, 200, "2026-11-19", [])
        self.assertEqual(rec["status"], "new binary baseline")
        self.assertFalse(rec["review_pending"])
        self.assertIn("not a verification", rec["baseline_note"])
        monitor.update_success(rec, raw + b"B", 200, "2026-11-20", [])
        self.assertEqual(rec["status"], "changed")
        self.assertTrue(rec["review_pending"])

    def test_structure_sheet_change_marks_the_row_even_after_a_failure(self):
        url = "https://www.venetianlasvegas.com/structure.pdf"
        with mock.patch.object(build_site, "monitor", {"urls": [
            {"url": url, "status": "unreachable", "review_pending": True}]}):
            self.assertIn("review pending", build_site.changed_flag("https://example.com/schedule", url))

    def test_registry_finds_nested_official_citations(self):
        url = "https://www.venetianlasvegas.com/deeply-nested-source"
        found = build_monitor_registry.collect({"events": [{"rules_fields": {"fee": {"source_url": url}}}]})
        self.assertIn(url, found)

    def test_refresh_publishes_report_only_after_rebase_and_stops_on_conflict(self):
        script = Path(__file__).resolve().parent / "commit-refresh.sh"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "site-data").mkdir()
            (root / "site-data/change-report.json").write_text('{"needs_attention": 1}')
            (root / "bin").mkdir()
            fake_git = root / "bin/git"
            fake_git.write_text('''#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$LOG"
if [ "$1" = rev-parse ]; then
  if [ "${2:-}" = --show-toplevel ]; then printf '%s\\n' "$TEST_ROOT"; else echo oldhash; fi
  exit 0
fi
if [ "$1" = diff ]; then exit 1; fi
if [ "$1" = pull ] && [ "${FAIL_REBASE:-}" = 1 ]; then exit 1; fi
exit 0
''')
            fake_git.chmod(0o755)
            env = dict(os.environ, PATH=str(root / "bin") + ":" + os.environ["PATH"],
                       TEST_ROOT=d, LOG=str(root / "log"), GITHUB_REF_NAME="arena/test")
            ok = subprocess.run(["bash", str(script)], cwd=d, env=env, capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            calls = (root / "log").read_text().splitlines()
            pull = next(i for i, line in enumerate(calls) if line.startswith("pull --rebase"))
            push = next(i for i, line in enumerate(calls) if line.startswith("push origin"))
            self.assertLess(pull, push)
            self.assertIn("HEAD:refs/heads/arena/test", calls[push])
            self.assertFalse(any(line.startswith("checkout") for line in calls))
            (root / "log").write_text("")
            env["FAIL_REBASE"] = "1"
            failed = subprocess.run(["bash", str(script)], cwd=d, env=env, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertNotIn("push origin", (root / "log").read_text())


if __name__ == "__main__":
    unittest.main()
