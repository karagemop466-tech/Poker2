"""Shared, conservative source-change review state.

A repeated hash or a failed request does not re-verify any transcribed value. A
change stays open until a reviewer records the *exact* URL, hash and hash method
in data/source_reviews.json after reading the official document.
"""
from __future__ import annotations

import json
from pathlib import Path

REVIEW_FILE = Path(__file__).resolve().parent.parent / "data" / "source_reviews.json"


def load_reviews(path=REVIEW_FILE):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data.get("reviews", []) if isinstance(data, dict) else []
    except (OSError, ValueError):
        return []


def legacy_pending(record):
    """Read new state, or conservatively migrate old changed-on markers."""
    if "review_pending" in record:
        return bool(record["review_pending"])
    if "review_required" in record:
        return bool(record["review_required"])
    return bool(record.get("changed_on") or record.get("last_changed") or record.get("review_since")
                or record.get("status") == "changed" or record.get("change") == "CHANGED")


def has_review(reviews, url, digest, method):
    """Only a documented review of this exact content can clear a warning."""
    return bool(digest and method and any(
        r.get("url") == url and r.get("hash") == digest and r.get("hash_method") == method
        and r.get("reviewed_at") and r.get("reviewer") and r.get("note")
        for r in reviews if isinstance(r, dict)
    ))


def review_state(prior, changed, timestamp, url, digest, method, reviews):
    """Return (pending, since); failure must be passed with digest=None."""
    pending = legacy_pending(prior) or changed
    since = prior.get("pending_since") or prior.get("changed_on")
    if changed and not since:
        since = timestamp
    if digest and has_review(reviews, url, digest, method):
        return False, None
    return pending, since
