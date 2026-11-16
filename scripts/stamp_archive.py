#!/usr/bin/env python3
"""Insert a 'superseded' banner at the top of every archived page.

Idempotent: re-running replaces the existing banner rather than stacking a
second one. Run after any change to archive/.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = "<!--ARCHIVE-BANNER-->"

BANNER = MARK + """
<div style="position:fixed;left:0;right:0;bottom:0;z-index:99999;background:#2b1113;
border-top:2px solid #e8564f;color:#f4dede;font:13px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
padding:9px 16px;text-align:center">
<b style="color:#ff8a80">SUPERSEDED SITE.</b>
This dashboard has been replaced. Its buy-ins, guarantees and fees were typed by hand and are not
traceable to a source — at least one figures is wrong. Kept only as an audit trail.
<a href="/Poker2/index.html" style="color:#7fc4ff">Open the current dashboard →</a>
</div>
"""


def stamp(path, depth):
    html = open(path).read()
    if MARK in html:
        html = re.sub(re.escape(MARK) + r".*?</div>\s*", "", html, count=1, flags=re.S)
    prefix = "../" * depth
    banner = BANNER.replace("/Poker2/index.html", prefix + "index.html")
    if re.search(r"<body[^>]*>", html):
        html = re.sub(r"(<body[^>]*>)", r"\1" + banner, html, count=1)
    else:
        html = banner + html
    open(path, "w").write(html)
    return path


def main():
    n = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "archive", "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, os.path.join(ROOT, "archive"))
        depth = rel.count(os.sep) + 1  # every archived page sits at least one level down
        stamp(p, depth)
        n += 1
    print(f"stamped {n} archived pages")


if __name__ == "__main__":
    main()
