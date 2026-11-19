#!/usr/bin/env python3
"""Verify the published site: every internal link resolves, every external link points at an
official host, and every page carries the shared navigation.

    python3 scripts/check2026.py
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "2026"          # the consolidated surface lives under /2026/
SITE_ROOT = os.path.join(ROOT, SITE)

PAGES = [
    "index.html", "tournaments.html", "entry-rules.html", "schedule.html", "hotels.html",
    "walking.html", "trip.html", "venues.html", "venues/venetian.html", "venues/other.html",
    "venues/wynn.html", "venues/horseshoe.html", "venues/caesars-palace.html",
    "venues/bellagio.html", "venues/mgm-grand.html", "venues/resorts-world.html", "venues/westgate.html",
    "summary.html", "requirements.html", "questions.html", "suggestions.html", "flagged.html", "sources.html",
    "repo-review.html", "latest-review.html",
]

OFFICIAL_HOSTS = {
    "www.venetianlasvegas.com",
    "www.wynnlasvegas.com",
    "reservations.wynnlasvegas.com",
    "cdn.wynnresorts.com",
    "www.caesars.com",
    "bellagio.mgmresorts.com",
    "mgmgrand.mgmresorts.com",
    "assets.contentstack.io",
    "www.rwlasvegas.com",
    "www.westgateresorts.com",
    "www.clarkcountynv.gov",
}
# Link-out targets that are not citations: they let the reader confirm a route for themselves.
TOOL_HOSTS = {"www.google.com", "maps.apple.com", "www.openstreetmap.org"}

LINK = re.compile(r'(?:href|src)="([^"]+)"', re.I)


def main():
    errors = []
    checked = 0
    ext = 0
    for page in PAGES:
        path = os.path.join(SITE_ROOT, page)
        if not os.path.exists(path):
            errors.append("%s: file missing" % page)
            continue
        depth = os.path.dirname(page)
        with open(path, encoding="utf-8") as f:
            html_text = f.read()
        if 'href="index.html"' not in html_text and depth == "":
            errors.append("%s: missing navigation" % page)
        for url in LINK.findall(html_text):
            checked += 1
            if url.startswith("#"):
                if url != "#" and re.search(r'id=["\']%s["\']' % re.escape(url[1:]), html_text) is None:
                    errors.append("%s: dangling in-page anchor %s" % (page, url))
                continue
            if url.startswith(("http://", "https://")):
                ext += 1
                host = re.sub(r"^https?://", "", url).split("/")[0]
                if host not in OFFICIAL_HOSTS and host not in TOOL_HOSTS:
                    errors.append("%s: non-official external host %s (%s)" % (page, host, url))
                if url.startswith("http://"):
                    errors.append("%s: insecure link %s" % (page, url))
                continue
            if url.startswith(("mailto:", "tel:")):
                continue
            target = os.path.normpath(os.path.join(depth, url.split("#")[0]))
            if url.startswith("../"):
                # ''../'' walks up out of /2026/venues/ into /2026/, and from /2026/ into the
                # site root, which is a separate surface owned by another session.
                up = os.path.normpath(os.path.join(SITE_ROOT, depth, url.split("#")[0]))
                if up.startswith(SITE_ROOT + os.sep) or up == SITE_ROOT:
                    if not os.path.exists(up):
                        errors.append("%s: broken internal link -> %s" % (page, url))
                elif not os.path.exists(up):
                    errors.append("%s: broken cross-surface link -> %s" % (page, url))
                continue
            if not os.path.exists(os.path.join(SITE_ROOT, target)):
                errors.append("%s: broken internal link -> %s" % (page, url))
    # anchors referenced across pages
    for page in PAGES:
        path = os.path.join(SITE_ROOT, page)
        with open(path, encoding="utf-8") as f:
            html_text = f.read()
        depth = os.path.dirname(page)
        for m in re.finditer(r'href="([^"#]+\.html)#([^"]+)"', html_text):
            tgt, frag = m.group(1), m.group(2)
            if tgt.startswith("../"):
                up = os.path.normpath(os.path.join(SITE_ROOT, depth, tgt))
                if not (up.startswith(SITE_ROOT + os.sep) or up == SITE_ROOT):
                    continue
                if not os.path.exists(up):
                    errors.append("%s: cross-page link to missing file %s" % (page, tgt))
                    continue
                full = up
            depth = os.path.dirname(page)
            full = os.path.join(SITE_ROOT, os.path.normpath(os.path.join(depth, tgt)))
            if not os.path.exists(full):
                errors.append("%s: cross-page link to missing file %s" % (page, tgt))
                continue
            with open(full, encoding="utf-8") as g:
                if re.search(r'id=["\']%s["\']' % re.escape(frag), g.read()) is None:
                    errors.append("%s: %s#%s has no such anchor" % (page, tgt, frag))

    if errors:
        print("FAILED (%d problem(s) in %d links checked, %d external):" % (len(errors), checked, ext))
        for e in errors[:60]:
            print("  - " + e)
        return 1
    print("OK: %d pages, %d links (%d external citations), no broken links, "
          "no non-official hosts" % (len(PAGES), checked, ext))
    return 0


if __name__ == "__main__":
    sys.exit(main())
