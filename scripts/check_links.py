#!/usr/bin/env python3
"""Verify every generated page: internal links resolve, external links are official hosts.

Exit code 1 on any broken internal link or any non-official external host.
"""
import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFICIAL = (
    "venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com", "mgmresorts.com",
    "contentstack.io", "caesars.com", "github.com", "pokertda.com", "visitwynn.com",
    "rwlasvegas.com", "google.com", "apple.com",
)
PAGES = [
    "index.html", "tournaments.html", "schedule.html", "hotels.html", "venues.html",
    "single-entry.html", "summary.html", "questions.html", "suggestions.html",
    "flagged.html", "sources.html", "repo-review.html",
]
HREF = re.compile(r'href="([^"]+)"')


def main():
    pages = list(PAGES)
    vdir = os.path.join(ROOT, "venues")
    if os.path.isdir(vdir):
        pages += ["venues/" + f for f in sorted(os.listdir(vdir)) if f.endswith(".html")]

    errors, checked, external = [], 0, {}
    for page in pages:
        path = os.path.join(ROOT, page)
        if not os.path.exists(path):
            errors.append("missing page: " + page)
            continue
        html = open(path, encoding="utf-8").read()
        base = os.path.dirname(page)
        ids = set(re.findall(r'id="([^"]+)"', html))
        for href in HREF.findall(html):
            checked += 1
            if href.startswith("#"):
                if href[1:] and href[1:] not in ids:
                    errors.append("%s: dead in-page anchor %s" % (page, href))
                continue
            if href.startswith("mailto:") or href.startswith("tel:"):
                continue
            if href.startswith("http"):
                host = urlparse(href).netloc.lower()
                external[host] = external.get(host, 0) + 1
                if not any(host == h or host.endswith("." + h) for h in OFFICIAL):
                    errors.append("%s: non-official external host %s" % (page, href))
                continue
            # relative
            target = os.path.normpath(os.path.join(ROOT, base, href.split("#")[0]))
            if not os.path.exists(target):
                errors.append("%s: broken relative link %s" % (page, href))
            elif "#" in href:
                frag = href.split("#")[1]
                if frag:
                    tids = set(re.findall(r'id="([^"]+)"',
                                          open(target, encoding="utf-8").read()))
                    if frag not in tids:
                        errors.append("%s: dead cross-page anchor %s" % (page, href))

    print("pages checked: %d" % len(pages))
    print("hrefs checked: %d" % checked)
    print("external hosts:")
    for h, n in sorted(external.items(), key=lambda kv: -kv[1]):
        print("  %-38s %d" % (h, n))
    if errors:
        print("\nFAILED (%d):" % len(errors))
        for e in errors:
            print("  - " + e)
        return 1
    print("\nOK: no broken internal links, no non-official external hosts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
