#!/usr/bin/env python3
"""Small offline integrity check for the static GitHub Pages dashboard."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(ROOT.glob("*.html"))
OFFICIAL = ("venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com", "caesars.com")

class Checker(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = set()
        self.hrefs = []
        self.table_stack = []
        self.tbody_stack = []
        self.row = None
        self.required_rows = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        if tag == "table":
            self.table_stack.append("data-requires-source" in a)
        elif tag == "tbody":
            self.tbody_stack.append(any(self.table_stack))
        elif tag == "tr":
            self.row = {"required": bool(self.tbody_stack and self.tbody_stack[-1]), "links": []}
        elif tag == "a" and self.row is not None and a.get("href"):
            self.row["links"].append(a["href"])
    def handle_endtag(self, tag):
        if tag == "tr" and self.row is not None:
            if self.row["required"]:
                self.required_rows.append(self.row)
            self.row = None
        elif tag == "tbody" and self.tbody_stack:
            self.tbody_stack.pop()
        elif tag == "table" and self.table_stack:
            self.table_stack.pop()

errors=[]
parsed={}
for page in PAGES:
    parser=Checker(page)
    parser.feed(page.read_text(encoding="utf-8"))
    parsed[page.name]=parser

for page in PAGES:
    parser=parsed[page.name]
    for href in parser.hrefs:
        u=urlparse(href)
        if u.scheme in ("http", "https", "mailto", "tel"):
            continue
        target=(page.parent / u.path).resolve() if u.path else page.resolve()
        if not target.exists():
            errors.append(f"{page.name}: broken local link {href}")
        elif u.fragment and target.suffix==".html":
            target_parser=parsed.get(target.name)
            if target_parser and u.fragment not in target_parser.ids:
                errors.append(f"{page.name}: missing fragment #{u.fragment} in {target.name}")
    for i,row in enumerate(parser.required_rows,1):
        sources=[]
        for href in row["links"]:
            u=urlparse(href)
            host=(u.hostname or "").lower()
            if u.scheme=="https" and any(host==d or host.endswith("."+d) for d in OFFICIAL):
                sources.append(href)
        if not sources:
            errors.append(f"{page.name}: source-required table row {i} lacks an official HTTPS link")

if errors:
    print("SITE CHECK FAILED")
    print("\n".join("- "+e for e in errors))
    sys.exit(1)
print(f"SITE CHECK PASSED: {len(PAGES)} HTML pages; local links exist; {sum(len(p.required_rows) for p in parsed.values())} sourced table rows have official HTTPS links.")
